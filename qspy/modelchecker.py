import logging
import warnings
import numpy as np
from pysb.core import SelfExporter, MonomerPattern
from pysb.pattern import check_dangling_bonds, monomers_from_pattern, SpeciesPatternMatcher, RulePatternMatcher, ReactionPatternMatcher
from pysb.units.core import check as units_check
from core import Monomer, Parameter
from utils.logging import ensure_qspy_logging, LOGGER_NAME, log_event


class ModelChecker:
    def __init__(self, model=None, logger_name=LOGGER_NAME):
        self.model = model
        if model is None:
            self.model = SelfExporter.default_model
        ensure_qspy_logging()
        self.logger = logging.getLogger(logger_name)
        self.check()

    @log_event()
    def check(self):
        self.logger.info("🔍 Running ModelChecker...")
        self.check_unused_monomers()
        self.check_unused_parameters()
        self.check_zero_valued_parameters()
        self.check_missing_initial_conditions()
        # self.check_unconnected_species()
        # self.check_unbound_sites()
        # self.check_overdefined_rules()
        # self.check_unreferenced_expressions()
        # units_check(self.model)
        self.check_dangling_reused_bonds()
        self.check_units()

    def check_unused_monomers(self):
        used = set()
        for rule in self.model.rules:
            used.update(m.name for m in monomers_from_pattern(rule.rule_expression.reactant_pattern))
            # monomers_from_pattern doesn't handle None, so we need to 
            # check here or it will cause a problem with the set.union method.
            if rule.is_reversible:
                used.update(m.name for m in monomers_from_pattern(rule.rule_expression.product_pattern))

        unused = [m.name for m in self.model.monomers if m.name not in used]
        if len(unused) > 0:
            msg = f"Unused Monomers (not included in any Rules): {[m for m in unused]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    def check_unused_parameters(self):
        used = set()
        for rule in self.model.rules:
            if isinstance(rule.rate_forward, Parameter):
                used.add(rule.rate_forward.name)
            if rule.is_reversible:
                if isinstance(rule.rate_reverse, Parameter):
                    used.add(rule.rate_reverse.name)
        for ic in self.model.initials:
            if isinstance(ic.value, Parameter):
                used.add(ic.value.name)
        for expr in self.model.expressions:
            used.update(p.name for p in expr.expr.atoms(Parameter))

        unused = [p.name for p in self.model.parameters if p.name not in used]
        if unused:
            msg = f"Unused Parameters: {[p for p in unused]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    def check_zero_valued_parameters(self):
        zeros = [p for p in self.model.parameters if np.isclose(p.value, 0.0)]
        if zeros:
            msg = f"Zero-valued Parameters: {[p.name for p in zeros]}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    def check_missing_initial_conditions(self):
        defined = list()
        for initial in self.model.initials:
            for m in monomers_from_pattern(initial.pattern):
                defined.append(m.name)
        defined = set(defined)
        all_monomers = set(m.name for m in self.model.monomers)
        missing = all_monomers - defined
        if missing:
            msg = f"Monomers missing initial conditions: {list(missing)}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    
    def check_dangling_reused_bonds(self):
        for rule in self.model.rules:
            check_dangling_bonds(rule.rule_expression.reactant_pattern)
            if rule.is_reversible:
                check_dangling_bonds(rule.rule_expression.product_pattern)

    @log_event()
    def check_units(self):
        units_check(self.model)

    def check_unbound_sites(self):
        bound_sites = set()
        for r in self.model.rules:
            for cp in r.rule_expression().all_complex_patterns():
                for m in cp.monomer_patterns:
                    for site, state in m.site_conditions.items():
                        if isinstance(state, tuple):  # bond tuple
                            bound_sites.add((m.monomer.name, site))

        unbound = []
        for m in self.model.monomers:
            for site in m.sites:
                if (m.name, site) not in bound_sites:
                    unbound.append(f"{m.name}.{site}")

        if unbound:
            msg = f"Unbound Sites (never participate in bonds): {unbound}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)

    def check_overdefined_rules(self):
        seen = {}
        for r in self.model.rules:
            rxn = str(r.rule_expression())
            if rxn in seen:
                msg = f"Overdefined reaction: '{rxn}' in rules `{seen[rxn]}` and `{r.name}`"
                self.logger.warning(f"⚠️ {msg}")
                warnings.warn(msg, category=UserWarning)
            else:
                seen[rxn] = r.name

    def check_unreferenced_expressions(self):
        used = set()
        for rule in self.model.rules:
            if rule.rate_forward:
                used.update(str(p) for p in rule.rate_forward.parameters)
            if rule.rate_reverse:
                used.update(str(p) for p in rule.rate_reverse.parameters)
        for o in self.model.observables:
            used.update(str(p) for p in o.function.atoms(Parameter))

        exprs = [e.name for e in self.model.expressions if e.name not in used]
        if exprs:
            msg = f"Unreferenced Expressions: {exprs}"
            self.logger.warning(f"⚠️ {msg}")
            warnings.warn(msg, category=UserWarning)
