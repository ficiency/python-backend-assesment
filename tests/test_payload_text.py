import pytest

from app.payload_text import interleave, request_label, transform

LIST_1 = ["first string", "second string", "third string"]
LIST_2 = ["other string", "another string", "last string"]
EXPECTED = (
    "FIRST STRING, OTHER STRING, SECOND STRING, ANOTHER STRING, "
    "THIRD STRING, LAST STRING"
)


# The outside step turns each word into uppercase, as in the sample.
def test_a_word_is_turned_into_uppercase():
    assert transform("first string") == "FIRST STRING"


# The sample lists should come out in the exact mixed order from the task.
def test_sample_lists_become_the_expected_text():
    first = [transform(word) for word in LIST_1]
    second = [transform(word) for word in LIST_2]
    assert interleave(first, second) == EXPECTED


# Sending the same two lists again must point to the same stored payload.
def test_same_lists_keep_the_same_label():
    assert request_label(LIST_1, LIST_2) == request_label(list(LIST_1), list(LIST_2))


# One changed word is a different request, so it must not reuse the old payload.
def test_a_different_word_changes_the_label():
    changed = ["first string", "second string", "changed string"]
    assert request_label(LIST_1, LIST_2) != request_label(changed, LIST_2)


# Word order matters, because the mixed text would come out differently.
def test_a_different_order_changes_the_label():
    reversed_list = list(reversed(LIST_1))
    assert request_label(LIST_1, LIST_2) != request_label(reversed_list, LIST_2)


# The label is taken from the words as they arrived, before they are uppercased.
def test_the_label_uses_the_original_words():
    uppercase_1 = [transform(word) for word in LIST_1]
    uppercase_2 = [transform(word) for word in LIST_2]
    assert request_label(LIST_1, LIST_2) != request_label(uppercase_1, uppercase_2)


# The task only allows two lists of the same length, so mixing must stop.
def test_lists_of_different_length_are_rejected():
    with pytest.raises(ValueError):
        interleave(["one"], ["two", "three"])
