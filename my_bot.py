class MirrorBot:
    name = "mirror"

    def choose(self, rule_graph, history):
        if not history:
            return rule_graph.get_random_move()
        return history[-1][0]

BOT = MirrorBot()