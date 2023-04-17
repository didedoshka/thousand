from abc import abstractmethod


class Player():

    @abstractmethod
    def make_a_move(self, observation, info):
        pass
