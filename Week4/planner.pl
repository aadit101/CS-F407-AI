% planner.pl - Warehouse knowledge base (Logical Planning Lab, optional Prolog extension)
% Run with:  swipl planner.pl

% ---------- Task 6: warehouse facts and can_move ----------
connected(a,b).
connected(b,a).
connected(b,c).
connected(c,b).

can_move(X,Y) :- connected(X,Y).

% ---------- Task 7: plan verification ----------
valid_move(X,Y) :- connected(X,Y).

% Optional: check a whole route, e.g.  ?- valid_route([a,b,c]).
valid_route([_]).
valid_route([X,Y|Rest]) :- valid_move(X,Y), valid_route([Y|Rest]).

% ---------- Task 8: chain of inference ----------
wet_road.
slippery :- wet_road.
reduce_speed :- slippery.

% Example queries:
%   ?- can_move(a,b).        true.
%   ?- can_move(a,c).        false.
%   ?- valid_move(b,c).      true.
%   ?- valid_move(a,c).      false.
%   ?- valid_route([a,b,c]). true.
%   ?- valid_route([a,c]).   false.
%   ?- reduce_speed.         true.
