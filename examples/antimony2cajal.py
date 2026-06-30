"""
antimony2cajal: a blueprint frontend from SBML/Antimony reaction networks to Cajal
==================================================================================

A mass-action reaction network is a *multilinear* vector field

    dx/dt = N @ v(x)

where
    x      : species concentration vector            (n_species,)
    N      : stoichiometric matrix (species x rxns)  (n_species, n_rxns)
    v(x)   : reaction rate vector, each entry a monomial in x   (n_rxns,)

This is exactly the class Cajal compiles to a differentiable tensor program, and a
single explicit-Euler step is a fixed state->state map that `TmIter` unrolls in time.
This module shows the *general* path: extract (species, N, rate laws) from any SBML /
Antimony model, wrap one Euler step as the step function `f`, and run it inside the
compiled Cajal program  iter{ x0 | x -> f(x) }(n).

`from_antimony()` uses `tellurium`/`libantimony` when available. When it is not
installed (as in CI here), `reduced_abeta_tau_network()` returns the same structure
for the reduced Alzheimer's Aβ–tau core by hand, so the demo is always runnable.

NOTE (current limitations, see alzheimers_abeta_tau.py):
  * TmIter step count is a one-hot TyNat of dim 10 -> at most 9 in-graph steps.
  * Only explicit forward Euler; stiff models need implicit/adaptive solvers.
This is a structural blueprint, not a production importer.
"""

from dataclasses import dataclass
from typing import Callable

import torch
from torch import Tensor

from cajal.syntax import TmIter, TmVar, TmApp, TyNat, TyReal
from cajal.compiling import compile, TypedTensor

device = torch.device("cpu")


@dataclass
class ReactionNetwork:
    """A mass-action reaction network: dx/dt = N @ v(x)."""
    species: list[str]
    N: Tensor                              # (n_species, n_rxns) stoichiometric matrix
    rates: Callable[[Tensor], Tensor]      # x (n_species,) -> v (n_rxns,)

    def vector_field(self, x: Tensor) -> Tensor:
        return self.N @ self.rates(x)

    def conservation_laws(self) -> list[Tensor]:
        """Interpretable conserved moieties live in the left null space of N
        (vectors c with c^T N = 0). Returns an orthonormal basis."""
        u, s, _ = torch.linalg.svd(self.N, full_matrices=True)
        rank = int((s > 1e-6).sum())
        return [u[:, i] for i in range(rank, u.shape[0])]


# ── Frontend: Antimony/SBML -> ReactionNetwork ───────────────

def from_antimony(model_str: str) -> ReactionNetwork:
    """Parse an Antimony model into a ReactionNetwork via tellurium/libantimony.

    Requires `tellurium` (pip install tellurium). Raises ImportError with guidance
    if it is unavailable; use reduced_abeta_tau_network() for an offline demo.
    """
    try:
        import tellurium as te          # noqa: F401
    except ImportError as e:
        raise ImportError(
            "from_antimony() needs `tellurium` (pip install tellurium). "
            "For an offline demo use reduced_abeta_tau_network()."
        ) from e

    r = te.loada(model_str)
    species = list(r.getFloatingSpeciesIds())
    N = torch.tensor(r.getFullStoichiometryMatrix(), dtype=torch.float32, device=device)

    def rates(x: Tensor) -> Tensor:
        # Round-trip current state into the runtime and read reaction rates. A
        # production version would compile each rate law to a Cajal monomial term;
        # here we delegate to libroadrunner's evaluator.
        for sid, val in zip(species, x.tolist()):
            r[sid] = val
        return torch.tensor(r.getReactionRates(), dtype=torch.float32, device=device)

    return ReactionNetwork(species, N, rates)


def reduced_abeta_tau_network(
    k_agg=0.40, k_dis=0.05, k_phos=0.30, k_dephos=0.10
) -> ReactionNetwork:
    """The reduced Alzheimer's Aβ–tau core as a ReactionNetwork (offline fallback).

    Species : [Am, Ap, Tau, pTau]
    R1 (aggregation)     : Am -> Ap        rate = k_agg*Am - k_dis*Ap
    R2 (phosphorylation) : Tau -> pTau     rate = k_phos*Tau - k_dephos*pTau

    (k_phos is held constant here; alzheimers_abeta_tau.py makes it the learnable,
    plaque-dependent coupling k_phos(Ap).)
    """
    species = ["Am", "Ap", "Tau", "pTau"]
    N = torch.tensor([
        [-1., 0.],   # Am
        [ 1., 0.],   # Ap
        [ 0., -1.],  # Tau
        [ 0., 1.],   # pTau
    ], device=device)

    def rates(x: Tensor) -> Tensor:
        Am, Ap, Tau, pTau = x
        return torch.stack([
            k_agg * Am - k_dis * Ap,
            k_phos * Tau - k_dephos * pTau,
        ])

    return ReactionNetwork(species, N, rates)


# ── Compile a network to a Cajal program ─────────────────────

def euler_step(net: ReactionNetwork, dt: float):
    """Wrap one explicit-Euler step  x -> x + N v(x) dt  as a Cajal step function."""
    def f(state: TypedTensor) -> TypedTensor:
        x = state.data
        return TypedTensor(x + net.vector_field(x) * dt, state.ty)
    return f


def cajal_program():
    """The fixed program structure: iter{ x0 | x -> f(x) }(n)."""
    return TmIter(TmVar("x0"), "x", TmApp(TmVar("f"), TmVar("x")), TmVar("n"))


def simulate(net: ReactionNetwork, x0, n_steps: int, dt: float):
    """Run the compiled Cajal program for each step count 0..n_steps-1."""
    assert n_steps <= 10, "TmIter step count is a one-hot TyNat of dim 10 (max 9 steps)"
    compiled = compile(cajal_program())
    step_fn = euler_step(net, dt)
    x0_tt = TypedTensor(torch.tensor(x0, dtype=torch.float32, device=device),
                        TyReal(len(net.species)))
    traj = []
    for step in range(n_steps):
        n_onehot = torch.zeros(10, device=device)
        n_onehot[step] = 1.0
        res = compiled({"x0": x0_tt,
                        "f": lambda s, _f=step_fn: _f(s),
                        "n": TypedTensor(n_onehot, TyNat())})
        traj.append(res.data.tolist())
    return torch.tensor(traj)


if __name__ == "__main__":
    print("=" * 64)
    print("antimony2cajal: reduced Aβ–tau core  ->  Cajal program")
    print("=" * 64)

    try:
        net = from_antimony("""
        model abeta_tau_core
            Am  -> Ap;   k_agg*Am - k_dis*Ap;
            Tau -> pTau; k_phos*Tau - k_dephos*pTau;
            Am = 2; Ap = 0; Tau = 1; pTau = 0;
            k_agg = 0.4; k_dis = 0.05; k_phos = 0.3; k_dephos = 0.1;
        end
        """)
        print("loaded model via tellurium/libantimony")
    except ImportError as e:
        print(f"(tellurium unavailable: {e.args[0].splitlines()[0]})")
        print("falling back to hand-coded reduced network")
        net = reduced_abeta_tau_network()

    print(f"\nspecies: {net.species}")
    print("stoichiometric matrix N:")
    print(net.N.numpy())

    print("\nconservation laws (left null space of N):")
    rank = int(torch.linalg.matrix_rank(net.N))
    print(f"  {net.N.shape[0]} species - rank {rank} = {net.N.shape[0]-rank} conserved moieties")
    for c, name in [(torch.tensor([1., 1., 0., 0.]), "Am+Ap (total Aβ)"),
                    (torch.tensor([0., 0., 1., 1.]), "Tau+pTau (total tau)")]:
        print(f"  {name:22s}  c^T N = {(c @ net.N).abs().max().item():.1e}")

    dt, n = 0.3, 10
    traj = simulate(net, [2.0, 0.0, 1.0, 0.0], n_steps=n, dt=dt)
    print(f"\nsimulated {n} Euler steps (dt={dt}) via the compiled Cajal program:")
    print(f"  {'step':>4}  {'Am':>7} {'Ap':>7} {'Tau':>7} {'pTau':>7}  "
          f"{'Am+Ap':>7} {'Tau+pTau':>8}")
    for i, row in enumerate(traj):
        Am, Ap, Tau, pTau = row.tolist()
        print(f"  {i:>4}  {Am:7.4f} {Ap:7.4f} {Tau:7.4f} {pTau:7.4f}  "
              f"{Am+Ap:7.4f} {Tau+pTau:8.4f}")
    print("\n=> Am+Ap and Tau+pTau stay constant: conservation holds by construction.")
