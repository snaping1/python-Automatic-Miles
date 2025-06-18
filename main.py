class MealyError(Exception):
    pass


class MealyMachine:
    def __init__(self):
        self.state = 'a5'
        self.vars = {}
        self.v = 1
        self.states = {
            'a5': {
                'transitions': {
                    'loop': [
                        {'condition': ('t', 0),
                         'output': 'n1', 'target': 'a4'},
                        {'condition': ('t', 1),
                         'output': 'n1', 'target': 'a6'}
                    ]
                }
            },
            'a4': {
                'transitions': {
                    'loop': [
                        {'output': 'n0', 'target': 'a3'}
                    ]
                }
            },
            'a3': {
                'transitions': {
                    'drag': [
                        {'output': 'n0', 'target': 'a6'}
                    ]
                }
            },
            'a6': {
                'transitions': {
                    'drag': [
                        {'condition': ('a', 1),
                         'output': 'n0', 'target': 'a0'},
                        {'condition': ('a', 0),
                         'output': 'n0', 'target': 'a3'}
                    ],
                }
            },
            'a0': {
                'transitions': {
                    'place': [
                        {'condition': ('c', 1),
                         'output': 'n0', 'target': 'a2'},
                        {'condition': ('c', 0),
                         'output': 'n0', 'target': 'a6'}
                    ],
                }
            },
            'a2': {
                'transitions': {
                    'shade': [
                        {'output': 'n0', 'target': 'a1'}
                    ]
                }
            },
            'a1': {
                'transitions': {
                    'edit': [
                        {'output': 'n1', 'target': 'a6'}
                    ]
                }
            }
        }
        self.all_methods = set()
        for state_data in self.states.values():
            for method in state_data['transitions']:
                self.all_methods.add(method)
        self.graph = self._build_graph()
        self.in_degree = self._compute_in_degree()
        self.max_degree = max(self.in_degree.values()) if self.in_degree else 0

    def _build_graph(self):
        graph = {state: set() for state in self.states}
        for state, state_data in self.states.items():
            for method, transitions in state_data['transitions'].items():
                for trans in transitions:
                    graph[state].add(trans['target'])
        return graph

    def _compute_in_degree(self):
        in_degree = {state: 0 for state in self.states}
        for state, targets in self.graph.items():
            for target in targets:
                in_degree[target] += 1
        return in_degree

    def set_var(self, name, value):
        self.vars[name] = value

    def __getattr__(self, name):
        if name in self.all_methods:
            def method():
                return self._handle_transition(name)

            return method
        else:
            raise MealyError('unknown')

    def _handle_transition(self, method_name):
        state_data = self.states[self.state]
        transitions = state_data['transitions'].get(method_name, [])
        if not transitions:
            raise MealyError('unsupported')

        chosen_trans = None

        chosen_trans = self._find_conditional_transition(transitions)

        if chosen_trans is None:
            chosen_trans = self._find_fallback_transition(transitions)

        if chosen_trans is None:
            raise MealyError('unsupported')

        self.state = chosen_trans['target']
        return chosen_trans['output']

    def _find_conditional_transition(self, transitions):
        for trans in transitions:
            if 'condition' in trans and self.v == 1:
                var_name, exp_value = trans['condition']
                if var_name in self.vars and self.vars[var_name] == exp_value:
                    return trans
        return None

    def _find_fallback_transition(self, transitions):
        for trans in transitions:
            if 'condition' not in trans or self.v == 0:
                return trans
        return None

    def has_max_in_edges(self):
        return self.in_degree[self.state] == self.max_degree

    def part_of_loop(self):
        return self.state in ['a0', 'a1', 'a2', 'a3', 'a6']


def main():
    return MealyMachine()


def test():
    obj = main()
    assert obj.set_var('a', 1) is None
    assert obj.part_of_loop() is False
    assert obj.set_var('t', 1) is None
    assert obj.part_of_loop() is False
    assert obj.has_max_in_edges() is False
    assert obj.set_var('c', 0) is None
    assert obj.loop() == 'n1'
    assert obj.drag() == 'n0'
    assert obj.set_var('a', 0) is None
    assert obj.part_of_loop() is True
    assert obj.place() == 'n0'
    assert obj.has_max_in_edges() is True
    assert obj.drag() == 'n0'
    try:
        obj.melt()
    except MealyError as e:
        assert str(e) == 'unknown'
    try:
        obj.place()
    except MealyError as e:
        assert str(e) == 'unsupported'
    m = main()
    m.set_var('t', 2)
    try:
        m.loop()
    except MealyError as e:
        assert str(e) == 'unsupported'

    m = main()

    m.v = 0
    m.state = 'a6'
    m.set_var('a', 2)
    m.drag()

    obj = main()
    obj.v = 0
    assert obj.set_var('t', 1) is None
    assert obj.loop() == 'n1'

    obj = main()
    obj.v = 0
    assert obj.set_var('a', 1) is None
    assert obj.part_of_loop() is False
    assert obj.set_var('t', 1) is None
    assert obj.part_of_loop() is False
    assert obj.has_max_in_edges() is False
    assert obj.set_var('c', 0) is None
    assert obj.loop() == 'n1'

    try:
        obj.drag()
    except MealyError as e:
        assert str(e) == 'unsupported'
    obj.set_var('a', 0)
    obj.part_of_loop()