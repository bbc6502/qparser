from unittest import TestCase
from qparser import query, And, Or, Not, Has, Near, Sequence, Exact, Context


class TestParser(TestCase):

    # One Item

    def test_sequence_a(self):
        assert query("a") == Sequence("a")

    def test_bounded_sequence_a(self):
        assert query("( a )") == Sequence("a")

    def test_and_a(self):
        assert query("AND a") == And("a")

    def test_bounded_and_a(self):
        assert query("{ a }") == And("a")

    def test_or_a(self):
        assert query("OR a") == Or("a")

    def test_bounded_or_a(self):
        assert query("[ a ]") == Or("a")

    def test_not_a(self):
        assert query("NOT a") == Not("a")

    def test_not_b(self):
        assert query("! b") == Not("b")

    def test_has_a(self):
        assert query("HAS a") == Has("a")

    def test_near_a(self):
        assert query("NEAR a") == Near("a")

    # Two items

    def test_a_and_b(self):
        assert query("a AND b") == And("a", "b")

    def test_bounded_and_a_b(self):
        assert query("{ a b }") == And("a", "b")

    def test_a_or_b(self):
        assert query("a OR b") == Or("a", "b")

    def test_bounded_or_a_b(self):
        assert query("[ a b ]") == Or("a", "b")

    def test_a_not_b(self):
        assert query("a NOT b") == Sequence("a", Not("b"))

    def test_not_a_not_b(self):
        assert query("NOT a NOT b") == Sequence(Not("a"), Not("b"))

    def test_not_a_and_not_b(self):
        assert query("NOT a AND NOT b") == And(Not("a"), Not("b"))

    def test_not_a_b(self):
        assert query("! a b") == Not(Sequence("a", "b"))

    def test_quoted_a_b(self):
        assert query('"a b"') == Exact(Sequence("a", "b"))

    def test_single_quoted_a_b(self):
        assert query("'a b'") == Exact(Sequence("a", "b"))

    def test_a_has_b(self):
        assert query("a HAS b") == Sequence("a", Has("b"))

    def test_a_near_b(self):
        assert query("a NEAR b") == Near("a", "b")

    # Three Items

    def test_a_and_b_and_c(self):
        assert query("a AND b AND c") == And("a", "b", "c")

    def test_bounded_and_a_b_c(self):
        assert query("{ a b c }") == And("a", "b", "c")

    def test_a_or_b_or_c(self):
        assert query("a OR b OR c") == Or("a", "b", "c")

    def test_bounded_or_a_b_c(self):
        assert query("[ a b c ]") == Or("a", "b", "c")

    def test_sequence_a_b_c(self):
        assert query("a b c") == Sequence("a", "b", "c")

    def test_bounded_sequence_a_b_c(self):
        assert query("( a b c )") == Sequence("a", "b", "c")

    def test_quoted_a_b_c(self):
        assert query('"a b c"') == Exact(Sequence("a", "b", "c"))

    def test_single_quoted_a_b_c(self):
        assert query("'a b c'") == Exact(Sequence("a", "b", "c"))

    # Sequence combinations

    def test_a_and_b_c(self):
        assert query("a AND b c") == And("a", Sequence("b", "c"))

    def test_a_or_b_c(self):
        assert query("a OR b c") == Or("a", Sequence("b", "c"))

    def test_a_has_b_c(self):
        assert query("a HAS b c") == Sequence("a", Has(Sequence("b", "c")))

    def test_a_near_b_c(self):
        assert query("a NEAR b c") == Near("a", Sequence("b", "c"))

    def test_not_a_b_2(self):
        assert query("NOT a b") == Not(Sequence("a", "b"))

    # Embedded within bounded and

    def test_bounded_and_a_b_and_c_3(self):
        assert query("{ a b AND c }") == And("a", "b", "c")

    def test_bounded_and_a_b_or_c_2(self):
        assert query("{ a b OR c }") == And("a", Or("b", "c"))

    def test_bounded_and_a_b_not_c_2(self):
        assert query("{ a b NOT c }") == And("a", "b", Not("c"))

    def test_bounded_and_a_b_has_c_2(self):
        assert query("{ a b HAS c }") == And("a", "b", Has("c"))

    def test_bounded_and_a_b_near_c_2(self):
        assert query("{ a b NEAR c }") == And("a", Near("b", "c"))

    # Embedded within bounded or

    def test_bounded_or_a_b_and_c_2(self):
        assert query("[ a b AND c ]") == Or("a", And("b", "c"))

    def test_bounded_or_a_b_or_c_2(self):
        assert query("[ a b OR c ]") == Or("a", "b", "c")

    def test_bounded_or_a_b_not_c_2(self):
        assert query("[ a b NOT c ]") == Or("a", "b", Not("c"))

    def test_bounded_or_a_b_has_c_2(self):
        assert query("[ a b HAS c ]") == Or("a", "b", Has("c"))

    def test_bounded_or_a_b_near_c_2(self):
        assert query("[ a b NEAR c ]") == Or("a", Near("b", "c"))

    # Embedded within bounded not

    def test_not_a_b_and_c_2(self):
        assert query("! a b AND c") == Not(And(Sequence("a", "b"), "c"))

    def test_not_a_b_or_c_2(self):
        assert query("! a b OR c") == Not(Or(Sequence("a", "b"), "c"))

    def test_not_a_b_not_c_3(self):
        assert query("! a b NOT c") == Not(Sequence("a", "b", Not("c")))

    def test_not_a_b_near_c_2(self):
        assert query("! a b NEAR c") == Not(Near(Sequence("a", "b"), "c"))

    # Other Combinations

    def test_bounded_or_a_b_and_c(self):
        assert query("[ a b ] AND c") == And(Or("a", "b"), "c")

    def test_has_a_has_b(self):
        assert query("HAS a HAS b") == Sequence(Has("a"), Has("b"))

    def test_a_has_b_has_c(self):
        assert query("a HAS b HAS c") == Sequence("a", Has("b"), Has("c"))

    def test_near_a_near_b(self):
        assert query("NEAR a NEAR b") == Near("a", "b")

    def test_a_and_b_or_c(self):
        assert query("a AND b OR c") == Or(And("a", "b"), "c")

    def test_a_and_b_or_c_d(self):
        assert query("a AND b OR c d") == Or(And("a", "b"), Sequence("c", "d"))

    def test_a_and_b_or_c_not_d(self):
        assert query("a AND b OR c NOT d") == Or(And("a", "b"), "c", Not("d"))

    def test_a_and_bounded_b_or_c_not_d_e(self):
        assert query("a AND (b OR c) NOT d e") == And("a", Or("b", "c"), Not(Sequence("d", "e")))

    def test_a_and_b_or_c_d_and_e_f(self):
        assert query("a AND b OR c d AND e f") == Or(And("a", "b"), And(Sequence("c", "d"), Sequence("e", "f")))

    def test_a_b_or_c_d_and_e_f(self):
        assert query("a b OR c d AND e f") == Or(Sequence("a", "b"), And(Sequence("c", "d"), Sequence("e", "f")))

    def test_other(self):
        assert query("[ a b ] c") == Sequence(Or("a", "b"), "c")

    def test_other_2(self):
        assert query("[ [ a b ] ] c") == Sequence(Or(Or("a", "b", bounded=True), bounded=True), "c")

    def test_other_3(self):
        assert query("(a OR b) OR c d") == Or(Or("a", "b"), Sequence("c", "d"))

    def test_other_4(self):
        assert query("(AND a)") == And("a")

    # Non alpha tokens

    def test_non_alpha(self):
        assert query("a,b") == Sequence("a", ",", "b")

    def test_non_alpha_2(self):
        assert query("a &= b") == Sequence("a", "&=", "b")

    # Representations

    def test_repr_sequence(self):
        assert repr(Sequence("a")) == "( 'a' )"

    def test_repr_sequence_2(self):
        assert repr(Sequence("a", "b")) == "( 'a' 'b' )"

    def test_repr_and(self):
        assert repr(And("a")) == "{ 'a' }"

    def test_repr_and_2(self):
        assert repr(And("a", "b")) == "{ 'a' 'b' }"

    def test_repr_or(self):
        assert repr(Or("a")) == "[ 'a' ]"

    def test_repr_or_2(self):
        assert repr(Or("a", "b")) == "[ 'a' 'b' ]"

    def test_repr_not(self):
        assert repr(Not("a")) == "! 'a'"

    def test_repr_has(self):
        assert repr(Has("a")) == "HAS 'a'"

    def test_repr_has_2(self):
        assert repr(Has("a", "b")) == "'a' HAS 'b'"

    def test_repr_near(self):
        assert repr(Near("a")) == "NEAR 'a'"

    def test_repr_near_2(self):
        assert repr(Near("a", "b")) == "'a' NEAR 'b'"

    def test_repr_exact(self):
        assert repr(Exact("a")) == "\" 'a' \""

    def test_repr_exact_2(self):
        assert repr(Exact("a", "b")) == "\" 'a' 'b' \""

    def test_repr_context(self):
        assert repr(Context(And("a", bounded=True))) == "{ 'a' }"

    def test_repr_context_2(self):
        assert repr(Context(And("a", bounded=True), Or("b", bounded=True))) == "{ 'a' } [ 'b' ]"

    # Compare Equals

    def test_equals_and(self):
        assert And("a", "b") == And("a", "b")

    def test_equals_or(self):
        assert Or("a", "b") == Or("a", "b")

    def test_equals_not(self):
        assert Not("a") == Not("a")

    def test_equals_sequence(self):
        assert Sequence("a", "b") == Sequence("a", "b")

    def test_equals_has(self):
        assert Has("a", "b") == Has("a", "b")

    def test_equals_near(self):
        assert Near("a", "b") == Near("a", "b")

    def test_equals_exact(self):
        assert Exact("a", "b") == Exact("a", "b")

    # Compare Not Equals

    def test_not_equals_and(self):
        assert And("a") != Or("a")

    def test_not_equals_or(self):
        assert Or("a") != Not("a")

    def test_not_equals_not(self):
        assert Not("a") != And("a")

    def test_not_equals_sequence(self):
        assert Sequence("a") != And("a")

    def test_not_equals_has(self):
        assert Has("a") != And("a")

    def test_not_equals_near(self):
        assert Near("a") != And("a")

    def test_not_equals_exact(self):
        assert Exact("a") != And("a")
