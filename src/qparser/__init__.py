from typing import List, Tuple, Union


class Parser:
    """Parse a query expression into a graph of terms"""

    def parse(self, query_expr: str) -> 'Term':
        """
        Parse a query expression to produce a graph of terms
        :param query_expr: the query to parse
        :return: graph of terms
        """
        index = 0
        context = Context(Sequence())
        prior = None
        while index < len(query_expr):
            if query_expr[index].isspace():
                index += 1
            elif query_expr[index].isalnum():
                index, token = self._parse_alpha_numeric_token(index, query_expr)
                token = self._process_alpha_token(context, prior, token)
                prior = token
            elif query_expr[index] == '"':
                index = self._process_exact_sequence(context, index, query_expr, '"')
            elif query_expr[index] == "'":
                index = self._process_exact_sequence(context, index, query_expr, "'")
            elif query_expr[index] == '(':
                index = self._process_start_bounded_terms(context, index, Sequence)
            elif query_expr[index] == ')':
                index, sequence = self._process_end_bounded_terms(context, index, Sequence)
                self._unwrap_singular_sequence(context, sequence)
            elif query_expr[index] == '{':
                index = self._process_start_bounded_terms(context, index, And)
            elif query_expr[index] == '}':
                index, _ = self._process_end_bounded_terms(context, index, And)
            elif query_expr[index] == '[':
                index = self._process_start_bounded_terms(context, index, Or)
            elif query_expr[index] == ']':
                index, _ = self._process_end_bounded_terms(context, index, Or)
            elif query_expr[index] == '!':
                index += 1
                self._process_unary_token(context, Not)
            else:
                index = self._parse_other_token(context, index, query_expr)
        return self._normalise_result(context)

    def _process_alpha_token(self, context: 'Context', prior: str, token: str) -> Union[str, 'Term']:
        if token == "AND":
            token = self._process_binary_token(context, And)
        elif token == "OR":
            token = self._process_binary_token(context, Or)
        elif token == "NEAR":
            token = self._process_binary_token(context, Near)
        elif token == "NOT":
            token = self._process_unary_token(context, Not)
        elif token == "HAS":
            token = self._process_unary_token(context, Has)
        else:
            self._ensure_sequence_unless_bounded(context, prior)
            context.current_context().append(token)
        return token

    @staticmethod
    def _normalise_result(context: 'Context') -> 'Term':
        result = context.first_context()
        normal = result.normalise()
        while result != normal:
            if isinstance(normal, str):
                return result
            result = normal
            normal = result.normalise()
        return normal

    @staticmethod
    def _unwrap_singular_sequence(context: 'Context', sequence: 'Term'):
        if len(sequence) == 1:
            context.current_context().replace_last(sequence[0])

    @staticmethod
    def _process_unary_token(context: 'Context', token_class) -> 'Term':
        """Token consisting of token RHS"""
        if isinstance(context.current_context(), token_class):
            context.pop_current_context()
        token = token_class()
        context.push_new_context(token)
        return token

    @staticmethod
    def _process_binary_token(context: 'Context', token_class) -> 'Term':
        """Token consisting of LHS token RHS"""
        token = context.current_context()
        if not isinstance(token, token_class):
            token = context.encapsulate_lhs_with(token_class())
        return token

    @staticmethod
    def _process_start_bounded_terms(context: 'Context', index: int, token_class) -> int:
        index += 1
        token = token_class(bounded=True)
        context.push_new_context(token)
        return index

    @staticmethod
    def _process_end_bounded_terms(context: 'Context', index: int, token_class) -> Tuple[int, 'Term']:
        index += 1
        while not isinstance(context.current_context(), token_class) or not context.is_bounded():
            context.pop_current_context()
        term = context.pop_current_context()
        return index, term

    @staticmethod
    def _parse_alpha_numeric_token(index: int, query_expr: str) -> Tuple[int, str]:
        """Parse a token consisting of alphanumeric characters"""
        start_index = index
        index += 1
        while index < len(query_expr) and query_expr[index].isalnum():
            index += 1
        token = query_expr[start_index:index]
        return index, token

    @staticmethod
    def _parse_other_token(context: 'Context', index: int, query_expr: str) -> int:
        """Parse a token that isn't a special character or alphanumeric token"""
        start_index = index
        index += 1
        while index < len(query_expr) \
                and not query_expr[index].isalnum() \
                and not query_expr[index].isspace() and query_expr[index] not in "(){}[]!":
            index += 1
        token = query_expr[start_index:index]
        context.current_context().append(token)
        return index

    def _process_exact_sequence(self, context: 'Context', index: int, query_expr: str, end_token: str) -> int:
        """Parse terms inside an exact terms qualifier"""
        index += 1
        token = Exact(bounded=True)
        context.push_new_context(token)
        start_index = index
        while index < len(query_expr) and query_expr[index] != end_token:
            index += 1
        token = query_expr[start_index:index]
        context.current_context().append(self.parse(token))
        context.pop_current_context()
        index += 1
        return index

    @staticmethod
    def _ensure_sequence_unless_bounded(context: 'Context', prior: str) -> None:
        """If the prior was a string then ensure a sequence exists"""
        if isinstance(prior, str):
            if not context.is_bounded():
                if not isinstance(context.current_context(), Sequence):
                    sequence = Sequence()
                    context.current_context().encapsulate_last_with(sequence)
                    context.append(sequence)


def query(query_expr: str) -> 'Term':
    """
    Parse a query string and return a graph of the terms
    :param query_expr: the query expression to parse
    :return: the graph of terms
    """
    return Parser().parse(query_expr)


class Term:
    """
    A term expressed in the query string
    """
    def __init__(self, *terms, bounded=False):
        self.components: List[Term] = list(terms)
        self.bounded = bounded

    def append(self, term) -> 'Term':
        """Append a term as a component of this term"""
        self.components.append(term)
        return self

    def replace_last(self, term) -> None:
        """Replace the last component term with the term"""
        self.components[-1] = term

    def encapsulate_last_with(self, term) -> 'Term':
        """Encapsulate the last component term with this term"""
        if len(self.components) > 0:
            term.append(self.components[-1])
            self.components[-1] = term
        else:
            self.components.append(term)
        return self

    def __getitem__(self, item) -> 'Term':
        return self.components[item]

    def __len__(self):
        return len(self.components)

    def normalise(self) -> 'Term':
        return self


class And(Term):
    """
    term AND term
    """
    def __init__(self, *args, bounded=False):
        super().__init__(*args, bounded=bounded)

    def __repr__(self):
        return "{ " + " ".join([repr(arg) for arg in self.components]) + " }"

    def __eq__(self, other):
        if not isinstance(other, And):
            return False
        return self.components == other.components

    def normalise(self) -> 'Term':
        if len(self.components) == 1:
            return self.components[0]
        return self


class Or(Term):
    """
    term OR term
    """
    def __init__(self, *args, bounded=False):
        super().__init__(*args, bounded=bounded)

    def __repr__(self):
        return "[ " + " ".join([repr(arg) for arg in self.components]) + " ]"

    def __eq__(self, other):
        if not isinstance(other, Or):
            return False
        return self.components == other.components

    def normalise(self) -> 'Term':
        if len(self.components) == 1:
            return self.components[0]
        return self


class Not(Term):
    """
    NOT term
    """
    def __init__(self, *args):
        super().__init__(*args, bounded=False)

    def __repr__(self):
        return "! " + " ".join([repr(arg) for arg in self.components])

    def __eq__(self, other):
        if not isinstance(other, Not):
            return False
        return self.components == other.components


class Has(Term):
    """
    HAS term
    """
    def __init__(self, *args):
        super().__init__(*args, bounded=False)

    def __repr__(self):
        if len(self) == 1:
            return "HAS " + repr(self.components[0])
        return " HAS ".join([repr(arg) for arg in self.components])

    def __eq__(self, other):
        if not isinstance(other, Has):
            return False
        return self.components == other.components


class Near(Term):
    """
    term NEAR term
    """
    def __init__(self, *args, bounded=False):
        super().__init__(*args, bounded=bounded)

    def __repr__(self):
        if len(self) == 1:
            return "NEAR " + repr(self.components[0])
        return " NEAR ".join([repr(arg) for arg in self.components])

    def __eq__(self, other):
        if not isinstance(other, Near):
            return False
        return self.components == other.components

    def normalise(self) -> 'Term':
        if len(self.components) == 1:
            return self.components[0]
        return self


class Sequence(Term):
    """
    Sequence of terms
    """
    def __init__(self, *args, bounded=False):
        super().__init__(*args, bounded=bounded)

    def __repr__(self):
        return "( " + " ".join([repr(arg) for arg in self.components]) + " )"

    def __eq__(self, other):
        if not isinstance(other, Sequence):
            return False
        return self.components == other.components

    def normalise(self) -> 'Term':
        if len(self.components) == 1:
            return self.components[0]
        return self


class Exact(Term):
    """
    Exact terms
    """
    def __init__(self, *args, bounded=False):
        super().__init__(*args, bounded=bounded)

    def __repr__(self):
        return '" ' + " ".join([repr(arg) for arg in self.components]) + ' "'

    def __eq__(self, other):
        if not isinstance(other, Exact):
            return False
        return self.components == other.components


class Context:
    """
    Context of parsing
    """
    def __init__(self, *args):
        self.context: List[Term] = list(args)

    def __repr__(self):
        return ' '.join([repr(item) for item in self.context])

    def push_new_context(self, term: Term) -> None:
        self.current_context().append(term)
        self.context.append(term)

    def append(self, term: Term) -> None:
        self.context.append(term)

    def first_context(self) -> Term:
        return self.context[0]

    def current_context(self) -> Term:
        return self.context[-1]
    
    def is_bounded(self) -> bool:
        return self.context[-1].bounded

    def pop_current_context(self) -> Term:
        popped = self.context.pop()
        if len(self.context) == 0:
            self.context.append(Sequence([popped]))
        return popped

    def _encapsulate_current_context_with(self, term: Term) -> None:
        lhs = self.pop_current_context().normalise()
        if len(lhs) > 0:
            term.append(lhs)
        self.current_context().replace_last(term)

    def encapsulate_lhs_with(self, term: Term) -> Term:
        """
        If the LHS is a bounded context then encapsulate the last term of the current context
        , otherwise encapsulate the LHS context.
        Then make the encapsulating term the new current context.
        """
        context = self.current_context()
        if not context.bounded:
            self._encapsulate_current_context_with(term)
        else:
            context.encapsulate_last_with(term)
        self.append(term)
        return term
