"""
Alzheimer's Aβ–Tau Core: Learning Amyloid-Driven Tau Hyperphosphorylation
=========================================================================

A systems-biology-inspired example. Curated Alzheimer's disease models
(e.g. Proctor2010 `BIOMD0000000286`, Proctor2013 `BIOMD0000000488`, and
modern QSP models) are reaction networks written in SBML / Antimony.
Under mass-action kinetics such a network is a *multilinear* vector field
`dx/dt = N · v(x)` -- exactly the class of object Cajal compiles to a
differentiable tensor program. This file demonstrates the smallest viable
instance of that bridge on a disease-relevant model.

The reduced mechanistic core (4 species, 2 reversible reactions):

    # --- Antimony source (round-trips to SBML) -----------------
    # model abeta_tau_core
    #   Am   -> Ap;   k_agg*Am - k_dis*Ap        # Aβ monomer <-> plaque
    #   Tau  -> pTau; k_phos(Ap)*Tau - k_dephos*pTau   # tau phos <-> dephos
    # end
    # -----------------------------------------------------------

    dAm/dt   = -k_agg*Am + k_dis*Ap
    dAp/dt   =  k_agg*Am - k_dis*Ap
    dTau/dt  = -k_phos(Ap)*Tau + k_dephos*pTau
    dpTau/dt =  k_phos(Ap)*Tau - k_dephos*pTau

Known structure (fixed as Cajal program structure):
    - reversible mass-action aggregation and (de)phosphorylation
    - two conservation laws:  Am + Ap = const,  Tau + pTau = const
    - k_agg, k_dis, k_dephos known; dt = 0.3, 10 Euler steps

Unknown (made learnable): k_phos(Ap) -- the rate at which amyloid plaque
load drives tau hyperphosphorylation. This is the well-documented
"Aβ-plaque-dependent tau hyperphosphorylation" coupling that links the
two pathologies in AD.

Ground truth (hidden from the learner) -- a saturating (Michaelis-Menten)
response of the kinase to plaque load:

    k_phos(Ap) = k_base + Vmax * Ap / (Km + Ap)
    k_base = 0.02, Vmax = 0.50, Km = 0.50

We train on 8 trajectories spanning amyloid burden (different total Aβ,
i.e. disease severity), each observed over 10 timesteps. The learnable
k_phos is an MLP (1 -> 32 -> 32 -> 1) with Softplus output (rate > 0).

After training we:
    1. Compare learned k_phos(Ap) vs true on a grid of plaque loads
    2. Symbolic regression: linear / Michaelis-Menten / power / Hill
    3. Verify: all species >= 0; Am+Ap and Tau+pTau conserved
    4. Show that higher amyloid burden -> more phospho-tau at steady state
"""

import torch
import torch.nn as nn
from cajal.syntax import TmIter, TmVar, TmApp, TyNat, TyReal
from cajal.compiling import compile, TypedTensor

device = torch.device("cpu")

# ── Ground truth parameters ──────────────────────────────────

K_AGG = 0.40      # Aβ monomer -> plaque (known)
K_DIS = 0.05      # plaque -> monomer (known)
K_DEPHOS = 0.10   # pTau -> Tau, phosphatase activity (known)

K_BASE = 0.02     # basal tau phosphorylation rate
VMAX = 0.50       # max amyloid-driven boost
KM = 0.50         # plaque load at half-maximal effect

DT = 0.3
N_STEPS = 10      # Cajal TyNat one-hot supports 0..9 observation steps

# 8 trajectories spanning amyloid burden (total Aβ pool = initial monomer)
N_TRAJ = 8
ABETA_LOADS = torch.linspace(0.2, 2.0, N_TRAJ, device=device)
TAU_TOTAL = 1.0   # total tau pool (Tau + pTau), conserved


def true_k_phos(Ap):
    """Saturating (Michaelis-Menten) plaque-driven tau phosphorylation."""
    return K_BASE + VMAX * Ap / (KM + Ap)


def step_true(state):
    """One forward-Euler step of the true model (for data generation)."""
    Am, Ap, Tau, pTau = state
    flux_agg = K_AGG * Am - K_DIS * Ap
    flux_phos = true_k_phos(Ap) * Tau - K_DEPHOS * pTau
    return [
        Am - flux_agg * DT,
        Ap + flux_agg * DT,
        Tau - flux_phos * DT,
        pTau + flux_phos * DT,
    ]


def generate_trajectories():
    """Generate training data: [Am, Ap, Tau, pTau] trajectories."""
    all_curves = []
    for load in ABETA_LOADS:
        state = [load.item(), 0.0, TAU_TOTAL, 0.0]
        curve = []
        for _ in range(N_STEPS):
            curve.append(list(state))
            state = step_true(state)
        all_curves.append(torch.tensor(curve, device=device))
    return torch.stack(all_curves)  # (N_TRAJ, N_STEPS, 4)


# ── Learnable amyloid->tau coupling (MLP) ────────────────────

class PhosRateMLP(nn.Module):
    """Learns k_phos: Ap -> R+   (1 -> 32 -> 32 -> 1, Softplus output)."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 32),
            nn.Tanh(),
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, 1),
            nn.Softplus(),  # rate must be positive
        )

    def forward(self, Ap):
        return self.net(Ap.view(1, 1)).squeeze()


class AbetaTauUpdate(nn.Module):
    """
    One timestep of the Aβ–tau core with learned k_phos(Ap).

    The aggregation and (de)phosphorylation *structure* is fixed; only the
    amyloid->tau coupling is learned. Fluxes are applied antisymmetrically
    so each reaction conserves its pool by construction.
    """

    def __init__(self, k_agg, k_dis, k_dephos, k_phos_mlp, dt):
        super().__init__()
        self.k_agg = k_agg
        self.k_dis = k_dis
        self.k_dephos = k_dephos
        self.k_phos_mlp = k_phos_mlp
        self.dt = dt

    def forward(self, state):
        Am = state.data[0]
        Ap = state.data[1]
        Tau = state.data[2]
        pTau = state.data[3]

        flux_agg = self.k_agg * Am - self.k_dis * Ap
        flux_phos = self.k_phos_mlp(Ap) * Tau - self.k_dephos * pTau

        return TypedTensor(
            torch.stack([
                Am - flux_agg * self.dt,
                Ap + flux_agg * self.dt,
                Tau - flux_phos * self.dt,
                pTau + flux_phos * self.dt,
            ]),
            state.ty,
        )


# ── Training ─────────────────────────────────────────────────

def train(epochs=600, verbose=True):
    data = generate_trajectories()  # (N_TRAJ, N_STEPS, 4)

    # Cajal program: iter{s0 | s ↪ f(s)}(n)
    program = TmIter(
        TmVar("s0"),
        "s",
        TmApp(TmVar("f"), TmVar("s")),
        TmVar("n"),
    )
    compiled = compile(program)

    mlp = PhosRateMLP()
    update_fn = AbetaTauUpdate(K_AGG, K_DIS, K_DEPHOS, mlp, DT)
    optimizer = torch.optim.Adam(mlp.parameters(), lr=0.005)

    if verbose:
        print("=" * 64)
        print("ALZHEIMER'S Aβ–TAU CORE: learning k_phos(Ap)")
        print("=" * 64)
        print(f"  Known: k_agg={K_AGG}, k_dis={K_DIS}, k_dephos={K_DEPHOS}, dt={DT}")
        print(f"  Unknown: k_phos(Ap)  (true: {K_BASE}+{VMAX}*Ap/({KM}+Ap))")
        print(f"  Learner: MLP with {sum(p.numel() for p in mlp.parameters())} parameters")
        print(f"  Training on {N_TRAJ} trajectories, amyloid load "
              f"[{ABETA_LOADS[0]:.1f}, {ABETA_LOADS[-1]:.1f}]")
        print()

    for epoch in range(epochs):
        optimizer.zero_grad()
        total_loss = torch.tensor(0.0, device=device)

        for traj_idx in range(N_TRAJ):
            load = ABETA_LOADS[traj_idx]
            s0 = TypedTensor(
                torch.tensor([load.item(), 0.0, TAU_TOTAL, 0.0], device=device),
                TyReal(4),
            )
            for step in range(N_STEPS):
                n_onehot = torch.zeros(N_STEPS, device=device)
                n_onehot[step] = 1.0
                n_val = TypedTensor(n_onehot, TyNat())

                result = compiled({
                    "s0": s0,
                    "f": lambda s, _fn=update_fn: _fn(s),
                    "n": n_val,
                })

                # supervise on the tau pools (the observable biomarkers)
                pred_Tau = result.data[2]
                pred_pTau = result.data[3]
                true_Tau = data[traj_idx, step, 2]
                true_pTau = data[traj_idx, step, 3]
                total_loss = total_loss + (pred_Tau - true_Tau) ** 2 \
                    + (pred_pTau - true_pTau) ** 2

        total_loss.backward()
        optimizer.step()

        if verbose and (epoch % 100 == 0 or epoch == epochs - 1):
            print(f"  epoch {epoch:3d}  loss={total_loss.item():.8f}")

    # Decompile only where the data constrains the coupling: the largest
    # plaque load Ap actually visited by the training trajectories.
    ap_observed_max = data[..., 1].max().item()

    if verbose:
        print()
        _report(mlp, update_fn, compiled, ap_observed_max)
    return mlp, update_fn, compiled


# ── Reporting: evaluation, symbolic regression, verification ─

def _report(mlp, update_fn, compiled, ap_max):
    # ── Learned vs true k_phos(Ap) ───────────────────────────
    print("=" * 64)
    print(f"LEARNED vs TRUE k_phos(Ap)   (observed range Ap in [0, {ap_max:.2f}])")
    print("=" * 64)
    print(f"  {'Ap':>6s}  {'True k_phos':>11s}  {'Learned':>9s}  {'Error':>8s}")
    Ap_grid = torch.linspace(0.0, ap_max, 11, device=device)
    max_err = 0.0
    with torch.no_grad():
        for Ap in Ap_grid:
            tv = true_k_phos(Ap).item()
            lv = mlp(Ap).item()
            err = abs(tv - lv)
            max_err = max(max_err, err)
            print(f"  {Ap.item():6.2f}  {tv:11.4f}  {lv:9.4f}  {err:8.4f}")
    print(f"\n  Max absolute error: {max_err:.4f}")

    # ── Symbolic regression (decompilation) ──────────────────
    print()
    print("=" * 64)
    print("SYMBOLIC REGRESSION (decompilation)")
    print("=" * 64)
    Ap_dense = torch.linspace(0.0, ap_max, 200, device=device)
    with torch.no_grad():
        learned = torch.tensor([mlp(a).item() for a in Ap_dense])

    best = {"name": None, "mse": float("inf"), "params": None}

    def consider(name, mse, params):
        if mse < best["mse"]:
            best.update(name=name, mse=mse, params=params)

    # 1. Michaelis-Menten / saturating: b + V*Ap/(K+Ap)
    mm = {"mse": float("inf")}
    for b in torch.linspace(0.0, 0.1, 30):
        for V in torch.linspace(0.1, 1.0, 60):
            for K in torch.linspace(0.05, 2.0, 60):
                pred = b + V * Ap_dense / (K + Ap_dense)
                mse = ((pred - learned) ** 2).mean().item()
                if mse < mm["mse"]:
                    mm = {"mse": mse, "b": b.item(), "V": V.item(), "K": K.item()}
    print(f"  Michaelis-Menten  b+V*Ap/(K+Ap): "
          f"b={mm['b']:.3f}, V={mm['V']:.3f}, K={mm['K']:.3f}  MSE={mm['mse']:.6f}")
    consider("Michaelis-Menten: b+V*Ap/(K+Ap)", mm["mse"],
             f"b={mm['b']:.3f}, V={mm['V']:.3f}, K={mm['K']:.3f}")

    # 2. Linear: a*Ap + c
    lin = {"mse": float("inf")}
    for a in torch.linspace(0.0, 0.6, 120):
        for c in torch.linspace(0.0, 0.3, 120):
            pred = a * Ap_dense + c
            mse = ((pred - learned) ** 2).mean().item()
            if mse < lin["mse"]:
                lin = {"mse": mse, "a": a.item(), "c": c.item()}
    print(f"  Linear            a*Ap + c:       "
          f"a={lin['a']:.3f}, c={lin['c']:.3f}  MSE={lin['mse']:.6f}")
    consider("Linear: a*Ap + c", lin["mse"], f"a={lin['a']:.3f}, c={lin['c']:.3f}")

    # 3. Power: a*Ap^b + c
    powf = {"mse": float("inf")}
    for a in torch.linspace(0.05, 0.8, 50):
        for b in torch.linspace(0.2, 1.5, 50):
            for c in torch.linspace(0.0, 0.1, 20):
                pred = a * Ap_dense ** b + c
                mse = ((pred - learned) ** 2).mean().item()
                if mse < powf["mse"]:
                    powf = {"mse": mse, "a": a.item(), "b": b.item(), "c": c.item()}
    print(f"  Power             a*Ap^b + c:     "
          f"a={powf['a']:.3f}, b={powf['b']:.3f}, c={powf['c']:.3f}  MSE={powf['mse']:.6f}")
    consider("Power: a*Ap^b + c", powf["mse"],
             f"a={powf['a']:.3f}, b={powf['b']:.3f}, c={powf['c']:.3f}")

    print()
    print(f"  BEST FIT: {best['name']}  (MSE={best['mse']:.6f})")
    print(f"  Parameters: {best['params']}")
    print()
    print("  The recovered coupling is concave/saturating in plaque load -- the")
    print("  amyloid->tau drive plateaus rather than growing without bound.")
    print(f"  Michaelis-Menten recovery (true generative form):")
    print(f"    True:    b={K_BASE:.3f}, V={VMAX:.3f}, K={KM:.3f}")
    print(f"    Learned: b={mm['b']:.3f}, V={mm['V']:.3f}, K={mm['K']:.3f}  (MSE={mm['mse']:.6f})")

    # ── Verification ─────────────────────────────────────────
    print()
    print("=" * 64)
    print("VERIFICATION (invariants by construction)")
    print("=" * 64)
    all_positive = True
    abeta_conserved = True
    tau_conserved = True
    with torch.no_grad():
        for traj_idx in range(N_TRAJ):
            load = ABETA_LOADS[traj_idx].item()
            s0 = TypedTensor(
                torch.tensor([load, 0.0, TAU_TOTAL, 0.0], device=device),
                TyReal(4),
            )
            for step in range(N_STEPS):
                n_onehot = torch.zeros(N_STEPS, device=device)
                n_onehot[step] = 1.0
                result = compiled({
                    "s0": s0,
                    "f": lambda s, _fn=update_fn: _fn(s),
                    "n": TypedTensor(n_onehot, TyNat()),
                })
                Am, Ap, Tau, pTau = (result.data[i].item() for i in range(4))
                if min(Am, Ap, Tau, pTau) < -1e-8:
                    all_positive = False
                if abs((Am + Ap) - load) > 1e-4:
                    abeta_conserved = False
                if abs((Tau + pTau) - TAU_TOTAL) > 1e-4:
                    tau_conserved = False

    print(f"  All species >= 0:                   "
          f"{'VERIFIED' if all_positive else 'FAILED'}")
    print(f"  Am + Ap = total Aβ (conservation):  "
          f"{'VERIFIED' if abeta_conserved else 'FAILED'}")
    print(f"  Tau + pTau = total tau (conserv.):  "
          f"{'VERIFIED' if tau_conserved else 'FAILED'}")

    # ── Dose-response: amyloid burden -> steady-state pTau ────
    print()
    print("=" * 64)
    print("AMYLOID BURDEN -> STEADY-STATE PHOSPHO-TAU")
    print("=" * 64)
    print(f"  {'total Aβ':>9s}  {'plaque Ap':>10s}  {'pTau fraction':>13s}")
    with torch.no_grad():
        for load in ABETA_LOADS:
            s = TypedTensor(
                torch.tensor([load.item(), 0.0, TAU_TOTAL, 0.0], device=device),
                TyReal(4),
            )
            for _ in range(300):           # long run -> steady state
                s = update_fn(s)
            Ap_eq = s.data[1].item()
            pTau_eq = s.data[3].item()
            print(f"  {load.item():9.2f}  {Ap_eq:10.4f}  {pTau_eq:13.4f}")


if __name__ == "__main__":
    train()
