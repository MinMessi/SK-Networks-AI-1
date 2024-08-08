import tensorflow as tf

class LinearRegressionModel(tf.Module):

    def __init__(self):
        # super().__init__(name=name)
        # tf.Variable : 얘네들을 학습시켜서 최적의 값으로 계속 업데이트 시키겠다. == torch에서는 nn.parameter
        self.weight = tf.Variable(tf.random.uniform([1], -1.0, 1.0), trainable=True)
        self.intercept = tf.Variable(tf.zeros([1]), trainable=True)

    def __call__(self, x):
        # y = wX + b >> w,b가 최종적인 y에 가까워지도록 학습
        return self.weight * x + self.intercept # 해당 클래스를 호출한다면 회귀 식 반환