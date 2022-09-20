from typing import List

class CombinationCount(object):

    def __init__(self, max_items: int):
        limit = max_items + 1
        self.binomial_coefficients: List[List[int]] = [
            [0 for _ in range(limit)] for _ in range(limit)
        ]

        for i in range(limit):
            self.binomial_coefficients[i][0] = 1
            self.binomial_coefficients[i][i] = 1

        for i in range(1, limit):
            for j in range(1, i):
                self.binomial_coefficients[i][j] = (
                    self.binomial_coefficients[i - 1][j - 1] +
                    self.binomial_coefficients[i - 1][j]
                )

    def nCr(self, n: int, c: int) -> int:
        if c > n:
            raise ValueError("n >= c at all times")
        return self.binomial_coefficients[n][c]
