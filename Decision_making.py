# Import the necessary classes
import itertools

# Base class for logical sentences
class Sentence():

    def evaluate(self, model):
        raise Exception("nothing to evaluate")

    def formula(self):
        return ""

    def symbols(self):
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        def balanced(s):
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not len(s) or s.isalpha() or (
            s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])
        ):
            return s
        else:
            return f"({s})"


class Symbol(Sentence):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def __repr__(self):
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}


class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()


class And(Sentence):
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(
            ("and", tuple(hash(conjunct) for conjunct in self.conjuncts))
        )

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula())
                           for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])


class Or(Sentence):
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(
            ("or", tuple(hash(disjunct) for disjunct in self.disjuncts))
        )

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨  ".join([Sentence.parenthesize(disjunct.formula())
                            for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])


class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication)
                and self.antecedent == other.antecedent
                and self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def evaluate(self, model):
        return (not self.antecedent.evaluate(model)
                or self.consequent.evaluate(model))

    def formula(self):
        return f"{Sentence.parenthesize(self.antecedent.formula())} => {Sentence.parenthesize(self.consequent.formula())}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())


def model_check(knowledge, query):
    def check_all(knowledge, query, symbols, model):
        if not symbols:
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:
            remaining = symbols.copy()
            p = remaining.pop()
            model_true = model.copy()
            model_true[p] = True
            model_false = model.copy()
            model_false[p] = False
            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    symbols = set.union(knowledge.symbols(), query.symbols())
    return check_all(knowledge, query, symbols, dict())



Rain = Symbol("Rain")
HeavyTraffic = Symbol("HeavyTraffic")
EarlyMeeting = Symbol("EarlyMeeting")
Strike = Symbol("Strike")
Appointment = Symbol("Appointment")
RoadConstruction = Symbol("RoadConstruction")


WFH = Symbol("WorkFromHome")
Drive = Symbol("Drive")
PublicTransport = Symbol("PublicTransport")


# Base rules setup with each rule uniquely defined

# Rule 1: If it’s raining or there's an early meeting, then work from home
rule1 = Implication(Or(Rain, EarlyMeeting), WFH)

# Rule 2: If there’s an appointment and no early meeting, then drive
rule2 = Implication(And(Appointment, Not(EarlyMeeting)), Drive)

# Rule 3: If there’s no strike and it’s not raining, take public transport
rule3 = Implication(And(Not(Strike), Not(Rain)), PublicTransport)

# Knowledge base combining all rules
knowledge_base = And(rule1, rule2, rule3)

# Define the queries
query_wfh = WFH
query_drive = Drive
query_public_transport = PublicTransport


# Scenario model check function
def perform_model_check(model):
    print(f"Model: {model}")
    print(f"Should work from home? {model_check(knowledge_base, query_wfh)}")
    print(f"Should drive? {model_check(knowledge_base, query_drive)}")
    print(f"Should take public transport? {model_check(knowledge_base, query_public_transport)}")
    print()


# Scenario 1: It’s raining, and there’s heavy traffic
scenario1 = {
    "Rain": True,
    "HeavyTraffic": True,
    "EarlyMeeting": False,
    "Strike": False,
    "Appointment": False  # Adding all symbols used in rules
}
perform_model_check(scenario1)

# Scenario 2: There’s a public transport strike, and it’s not raining
scenario2 = {
    "Rain": False,
    "HeavyTraffic": False,
    "EarlyMeeting": False,
    "Strike": True,
    "Appointment": False  # Adding all symbols used in rules
}
perform_model_check(scenario2)

# Scenario 3: No rain, traffic is light, and there’s no strike
scenario3 = {
    "Rain": False,
    "HeavyTraffic": False,
    "EarlyMeeting": False,
    "Strike": False,
    "Appointment": False  # Adding all symbols used in rules
}
perform_model_check(scenario3)

# Scenario 4: No rain, Doctor's appointment, and should drive
scenario4 = {
    "Rain": False,
    "HeavyTraffic": False,
    "EarlyMeeting": False,
    "Strike": False,
    "Appointment": True,  # Doctor’s appointment present
    "RoadConstruction": False  # Not used in rules but defined
}
perform_model_check(scenario4)
