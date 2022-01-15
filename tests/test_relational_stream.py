import re
from typing import Optional

from relational_stream import Flow, RelationalStream


class SomeStringFlow(Flow[str]):
    """
    Simple flow example to identify a sequence of strings using regex. This flow will match a series
    of the events in the form::

        "start A"
        "A -> B or C"
        "B" OR "C"
    """

    first_char: Optional[str] = None
    second_char_options: Optional[set[str]] = None
    second_char_choice: Optional[str] = None

    EVENT_REGEXES = [
        r"start (\w)",
        r"(\w) -> (\w) or (\w)",
        r"(\w)",
    ]

    def is_next_event(self, event: str) -> bool:
        if len(self.events) == 0:
            match = re.match(self.EVENT_REGEXES[0], event)
            if match is None:
                return False
            self.first_char = match[1]
            return True

        elif len(self.events) == 1:
            match = re.match(self.EVENT_REGEXES[1], event)
            if match is None or match[1] != self.first_char:
                return False
            self.second_char_options = {match[2], match[3]}
            return True

        else:  # len(self.events) == 2
            assert self.second_char_options is not None
            match = re.match(self.EVENT_REGEXES[2], event)
            if match is None or match[1] not in self.second_char_options:
                return False
            self.second_char_choice = match[1]
            return True

    def is_complete(self) -> bool:
        return len(self.events) == 3


def test_relational_stream_one_complete_flow():
    stream = RelationalStream([SomeStringFlow])

    stream.ingest("start A")
    stream.ingest("A -> B or C")
    stream.ingest("B")

    assert len(stream.incomplete_flows(SomeStringFlow)) == 0
    assert len(stream.completed_flows(SomeStringFlow)) == 1
    assert stream.completed_flows(SomeStringFlow)[0].first_char == "A"
    assert stream.completed_flows(SomeStringFlow)[0].second_char_options == {"B", "C"}
    assert stream.completed_flows(SomeStringFlow)[0].second_char_choice == "B"


def test_relational_stream_one_complete_flow_with_extra():
    stream = RelationalStream([SomeStringFlow])

    stream.ingest("start A")
    stream.ingest("B")
    stream.ingest("A -> B or C")
    stream.ingest("A -> D or E")
    stream.ingest("B")

    assert len(stream.incomplete_flows(SomeStringFlow)) == 0
    assert len(stream.completed_flows(SomeStringFlow)) == 1
    assert stream.completed_flows(SomeStringFlow)[0].first_char == "A"
    assert stream.completed_flows(SomeStringFlow)[0].second_char_options == {"B", "C"}
    assert stream.completed_flows(SomeStringFlow)[0].second_char_choice == "B"


def test_relational_stream_two_complete_flows_interleaved():
    stream = RelationalStream([SomeStringFlow])

    stream.ingest("start A")
    stream.ingest("start D")
    stream.ingest("D -> E or F")
    stream.ingest("A -> B or C")
    stream.ingest("B")
    stream.ingest("F")

    assert len(stream.incomplete_flows(SomeStringFlow)) == 0
    assert len(stream.completed_flows(SomeStringFlow)) == 2
    assert stream.completed_flows(SomeStringFlow)[0].first_char == "A"
    assert stream.completed_flows(SomeStringFlow)[0].second_char_options == {"B", "C"}
    assert stream.completed_flows(SomeStringFlow)[0].second_char_choice == "B"
    assert stream.completed_flows(SomeStringFlow)[1].first_char == "D"
    assert stream.completed_flows(SomeStringFlow)[1].second_char_options == {"E", "F"}
    assert stream.completed_flows(SomeStringFlow)[1].second_char_choice == "F"


def test_relational_stream_one_complete_one_incomplete():
    stream = RelationalStream([SomeStringFlow])

    stream.ingest("start A")
    stream.ingest("start D")
    stream.ingest("D -> E or F")
    stream.ingest("A -> B or C")
    stream.ingest("F")

    assert len(stream.incomplete_flows(SomeStringFlow)) == 1
    assert len(stream.completed_flows(SomeStringFlow)) == 1
    assert stream.incomplete_flows(SomeStringFlow)[0].first_char == "A"
    assert stream.incomplete_flows(SomeStringFlow)[0].second_char_options == {"B", "C"}
    assert stream.incomplete_flows(SomeStringFlow)[0].second_char_choice is None
    assert stream.completed_flows(SomeStringFlow)[0].first_char == "D"
    assert stream.completed_flows(SomeStringFlow)[0].second_char_options == {"E", "F"}
    assert stream.completed_flows(SomeStringFlow)[0].second_char_choice == "F"
