"""
Smoke tests for all scientific examples.

Each test runs a reduced version of the example (fewer epochs) and
asserts that the learned parameters converge close to ground truth.
"""

import torch
import torch.nn as nn
import pytest
from cajal.syntax import TmIter, TmVar, TmApp, TyNat, TyReal
from cajal.compiling import compile, TypedTensor


@pytest.fixture
def compiled_iter():
    """The standard Cajal iteration program used by all examples."""
    program = TmIter(TmVar("s0"), "s", TmApp(TmVar("f"), TmVar("s")), TmVar("n"))
    return compile(program)


class TestExponentialDecay:
    TRUE_K = 0.3
    DT = 0.1
    C0 = 1.0
    N_STEPS = 10

    def test_recovers_rate(self, compiled_iter):
        true_decay = 1.0 - self.TRUE_K * self.DT
        cs_true = [self.C0 * (true_decay ** n) for n in range(self.N_STEPS)]

        w = nn.Parameter(torch.tensor([0.5]))

        def step(state):
            return TypedTensor(w * state.data, state.ty)

        optimizer = torch.optim.Adam([w], lr=0.01)
        c0 = TypedTensor(torch.tensor([self.C0]), TyReal(1))

        for _ in range(200):
            optimizer.zero_grad()
            loss = torch.tensor(0.0)
            for i in range(self.N_STEPS):
                n_oh = torch.zeros(self.N_STEPS)
                n_oh[i] = 1.0
                result = compiled_iter({"s0": c0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                loss = loss + (result.data[0] - cs_true[i]) ** 2
            loss.backward()
            optimizer.step()

        k_recovered = (1.0 - w.item()) / self.DT
        assert abs(k_recovered - self.TRUE_K) < 0.01


class TestDecayChain:
    def test_recovers_branching_ratios(self, compiled_iter):
        TRUE_F, TRUE_G = 0.7, 0.85
        LA, LB, LC, DT = 0.3, 0.1, 0.05, 0.5
        N_STEPS = 10

        # Generate ground truth
        true_data = []
        a, b, c, d = 1.0, 0.0, 0.0, 0.0
        for _ in range(N_STEPS):
            true_data.append(torch.tensor([a, b, c, d]))
            da = LA * a * DT
            db_in = TRUE_F * da
            dc_in_a = (1 - TRUE_F) * da
            db_out = LB * b * DT
            dc_in_b = TRUE_G * db_out
            dd_in = (1 - TRUE_G) * db_out + LC * c * DT
            a -= da
            b += db_in - db_out
            c += dc_in_a + dc_in_b - LC * c * DT
            d += dd_in

        f_raw = nn.Parameter(torch.tensor(0.0))
        g_raw = nn.Parameter(torch.tensor(0.0))

        def step(state):
            f = torch.sigmoid(f_raw)
            g = torch.sigmoid(g_raw)
            a, b, c, d = state.data[0], state.data[1], state.data[2], state.data[3]
            da = LA * a * DT
            a_new = a - da
            b_new = b + f * da - LB * b * DT
            c_new = c + (1 - f) * da + g * LB * b * DT - LC * c * DT
            d_new = d + (1 - g) * LB * b * DT + LC * c * DT
            return TypedTensor(torch.stack([a_new, b_new, c_new, d_new]), state.ty)

        optimizer = torch.optim.Adam([f_raw, g_raw], lr=0.05)
        s0 = TypedTensor(torch.tensor([1.0, 0.0, 0.0, 0.0]), TyReal(4))

        for _ in range(300):
            optimizer.zero_grad()
            loss = torch.tensor(0.0)
            for i in range(N_STEPS):
                n_oh = torch.zeros(N_STEPS)
                n_oh[i] = 1.0
                result = compiled_iter({"s0": s0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                loss = loss + ((result.data - true_data[i]) ** 2).sum()
            loss.backward()
            optimizer.step()

        assert abs(torch.sigmoid(f_raw).item() - TRUE_F) < 0.01
        assert abs(torch.sigmoid(g_raw).item() - TRUE_G) < 0.01

    def test_mass_conservation(self, compiled_iter):
        """Total A+B+C+D must be conserved."""
        f_raw = nn.Parameter(torch.tensor(0.5))
        g_raw = nn.Parameter(torch.tensor(1.0))
        LA, LB, LC, DT = 0.3, 0.1, 0.05, 0.5

        def step(state):
            f = torch.sigmoid(f_raw)
            g = torch.sigmoid(g_raw)
            a, b, c, d = state.data[0], state.data[1], state.data[2], state.data[3]
            da = LA * a * DT
            a_new = a - da
            b_new = b + f * da - LB * b * DT
            c_new = c + (1 - f) * da + g * LB * b * DT - LC * c * DT
            d_new = d + (1 - g) * LB * b * DT + LC * c * DT
            return TypedTensor(torch.stack([a_new, b_new, c_new, d_new]), state.ty)

        s0 = TypedTensor(torch.tensor([1.0, 0.0, 0.0, 0.0]), TyReal(4))
        with torch.no_grad():
            for i in range(10):
                n_oh = torch.zeros(10)
                n_oh[i] = 1.0
                result = compiled_iter({"s0": s0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                total = result.data.sum().item()
                assert abs(total - 1.0) < 1e-6, f"Mass not conserved at step {i}: {total}"


class TestChemicalKinetics:
    def test_mass_conservation(self, compiled_iter):
        """A + B must be conserved in reversible reaction."""
        k_rev = 0.1
        DT = 0.3

        mlp = nn.Sequential(nn.Linear(1, 16), nn.Tanh(), nn.Linear(16, 1), nn.Softplus())

        def step(state):
            a, b, T = state.data[0], state.data[1], state.data[2]
            k_fwd = mlp(T.view(1, 1)).squeeze()
            da = (-k_fwd * a + k_rev * b) * DT
            return TypedTensor(torch.stack([a + da, b - da, T]), state.ty)

        s0 = TypedTensor(torch.tensor([1.0, 0.0, 10.0]), TyReal(3))
        with torch.no_grad():
            for i in range(10):
                n_oh = torch.zeros(10)
                n_oh[i] = 1.0
                result = compiled_iter({"s0": s0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                total = result.data[0].item() + result.data[1].item()
                assert abs(total - 1.0) < 1e-6, f"Mass not conserved at step {i}: {total}"


class TestAlzheimersAbetaTau:
    """Reduced Aβ–tau core: two conservation laws and a learnable amyloid->tau coupling."""

    K_AGG, K_DIS, K_DEPHOS, DT = 0.40, 0.05, 0.10, 0.3
    K_BASE, VMAX, KM = 0.02, 0.50, 0.50
    N_STEPS = 10

    def _true_k_phos(self, Ap):
        return self.K_BASE + self.VMAX * Ap / (self.KM + Ap)

    def test_dual_conservation(self, compiled_iter):
        """Am+Ap and Tau+pTau are each conserved by construction (any k_phos)."""
        mlp = nn.Sequential(nn.Linear(1, 8), nn.Tanh(), nn.Linear(8, 1), nn.Softplus())

        def step(state):
            Am, Ap, Tau, pTau = (state.data[i] for i in range(4))
            flux_agg = self.K_AGG * Am - self.K_DIS * Ap
            flux_phos = mlp(Ap.view(1, 1)).squeeze() * Tau - self.K_DEPHOS * pTau
            return TypedTensor(torch.stack([
                Am - flux_agg * self.DT, Ap + flux_agg * self.DT,
                Tau - flux_phos * self.DT, pTau + flux_phos * self.DT]), state.ty)

        s0 = TypedTensor(torch.tensor([1.5, 0.0, 1.0, 0.0]), TyReal(4))
        with torch.no_grad():
            for i in range(self.N_STEPS):
                n_oh = torch.zeros(self.N_STEPS)
                n_oh[i] = 1.0
                r = compiled_iter({"s0": s0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                assert abs((r.data[0] + r.data[1]).item() - 1.5) < 1e-6
                assert abs((r.data[2] + r.data[3]).item() - 1.0) < 1e-6

    def test_recovers_saturating_coupling(self, compiled_iter):
        """Train the coupling on tau dynamics; recover a saturating k_phos(Ap)."""
        torch.manual_seed(0)
        loads = [0.4, 1.0, 1.8]

        def true_step(s):
            Am, Ap, Tau, pTau = s
            fa = self.K_AGG * Am - self.K_DIS * Ap
            fp = self._true_k_phos(Ap) * Tau - self.K_DEPHOS * pTau
            return [Am - fa * self.DT, Ap + fa * self.DT,
                    Tau - fp * self.DT, pTau + fp * self.DT]

        data = []
        for load in loads:
            s, curve = [load, 0.0, 1.0, 0.0], []
            for _ in range(self.N_STEPS):
                curve.append(list(s)); s = true_step(s)
            data.append(curve)

        mlp = nn.Sequential(nn.Linear(1, 16), nn.Tanh(), nn.Linear(16, 1), nn.Softplus())
        opt = torch.optim.Adam(mlp.parameters(), lr=0.01)

        def step(state):
            Am, Ap, Tau, pTau = (state.data[i] for i in range(4))
            fa = self.K_AGG * Am - self.K_DIS * Ap
            fp = mlp(Ap.view(1, 1)).squeeze() * Tau - self.K_DEPHOS * pTau
            return TypedTensor(torch.stack([
                Am - fa * self.DT, Ap + fa * self.DT,
                Tau - fp * self.DT, pTau + fp * self.DT]), state.ty)

        for _ in range(150):
            opt.zero_grad()
            loss = torch.tensor(0.0)
            for li, load in enumerate(loads):
                s0 = TypedTensor(torch.tensor([load, 0.0, 1.0, 0.0]), TyReal(4))
                for i in range(self.N_STEPS):
                    n_oh = torch.zeros(self.N_STEPS); n_oh[i] = 1.0
                    r = compiled_iter({"s0": s0, "f": step, "n": TypedTensor(n_oh, TyNat())})
                    loss = loss + (r.data[3] - data[li][i][3]) ** 2
            loss.backward(); opt.step()

        # Evaluate only within the observed plaque range (Ap up to ~1.2).
        with torch.no_grad():
            k = {a: mlp(torch.tensor([a]).view(1, 1)).squeeze().item()
                 for a in (0.2, 0.6, 1.0)}
        # increasing in plaque load
        assert k[1.0] > k[0.2]
        # saturating: stays below the Michaelis-Menten asymptote (k_base + Vmax)
        assert k[1.0] < self.K_BASE + self.VMAX
        # accurate against the hidden ground truth at well-observed points
        assert abs(k[0.6] - self._true_k_phos(torch.tensor(0.6)).item()) < 0.1
        assert abs(k[1.0] - self._true_k_phos(torch.tensor(1.0)).item()) < 0.1
