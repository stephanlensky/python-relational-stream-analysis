Python Relational Stream Analysis
=================================

A Python (3.9+) library for relational stream analysis. Define sequences ("flows") of events, each of which may depend on a previous event in the flow, and collect all such flows from a stream. This is particularly useful for analyzing network captures, as after identifying a certain flow of events (e.g. a series of network requests used to authenticate a user), this library can be used to easily filter out all such flows from a larger capture. This is highly resilient to extraneous requests occurring in the middle of long-running flows, so it can easily be used to target individual applications within complete network captures from system-wide MITM attacks.

Example
-------

It can be a bit hard to wrap your head around what this library does just from a written description, so let's take a look at a code example. The following shows a class which can be used to analyze a stream of strings, filtering out sequences with a predefined format. However, the included classes are fully generic, so a similar `Flow` could easily be created for a stream of HTTP requests.

::

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


   stream = RelationalStream([SomeStringFlow])

   stream.ingest("start A")
   stream.ingest("B")
   stream.ingest("A -> B or C")
   stream.ingest("A -> D or E")
   stream.ingest("B")

   # len(stream.incomplete_flows(SomeStringFlow)) == 0
   # len(stream.completed_flows(SomeStringFlow)) == 1
   # stream.completed_flows(SomeStringFlow)[0].first_char == "A"
   # stream.completed_flows(SomeStringFlow)[0].second_char_options == {"B", "C"}
   # stream.completed_flows(SomeStringFlow)[0].second_char_choice == "B"


As you can see, the addition of extraneous data in the middle of the stream has no effect on the completed flows. A need for this resilience when developing tools to analyze network captures was the primary motivation for developing this library.


Installation
------------

::

   pip3 install relational-stream


User Guide
----------

.. toctree::
   :maxdepth: 2

   api_reference
