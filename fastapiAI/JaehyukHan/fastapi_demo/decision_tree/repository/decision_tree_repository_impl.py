import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import tensorflow_decision_forests as tfdf

from decision_tree.repository.decision_tree_repository import DecisionTreeRepository


class DecisionTreeRepositoryImpl(DecisionTreeRepository):
    def loadWineInfo(self):
        return load_wine()

    def createDataFrame(self, data, featureNames):
        return pd.DataFrame(data=data, columns=featureNames)

    def splitTrainTestSet(self, wineDataFrame):
        return train_test_split(wineDataFrame, test_size=0.2, random_state=42)

    def applyStandardScaler(self, trainDataFrame, testDataFrame, featureName):
        scaler = StandardScaler()
        # 원래라면 fit 이후 transform을 해야함
        # 그러나 fit_transform은 이것을 한 번에 하도록 만들어줌
        # (사실 Domain 관점에서는 좀 문제가 있으나 제공해주는 라이브러리이므로 그냥 사용)

        # fit은 데이터를 분석하여 내부 파라미터를 학습하게 됨
        # transform은 학습된 내부 파라미터를 사용하여 데이터를 변환함
        # 고로 transform은 fit이 반드시 먼저 선행되어야 함
        trainDataFrame[featureName] = scaler.fit_transform(trainDataFrame[featureName])
        testDataFrame[featureName] = scaler.transform(testDataFrame[featureName])

        return trainDataFrame, testDataFrame

    def sliceTensor(self, scaledTrainDataFrame, scaledTestDataFrame):
        # from_tensor_slices()는 pandas에서 읽은 데이터를 Tensorflow 사용 primitives로 구성하기 위해 필요한 라이브러리입니다.
        # 결론적으로 pandas 데이터 -> Tensorflow 데이터로 만들 때 사용한다고 파악하면 됩니다.
        trainDataFrameAfterSlice = tf.data.Dataset.from_tensor_slices(
            (dict(scaledTrainDataFrame.drop('target', axis=1)),
            scaledTrainDataFrame["target"].astype(int))
        )
        testDataFrameAfterSlice = tf.data.Dataset.from_tensor_slices(
            (dict(scaledTestDataFrame.drop("target", axis=1)),
             scaledTestDataFrame["target"].astype(int))
        )

        return trainDataFrameAfterSlice, testDataFrameAfterSlice

    def applyBatchSize(self, trainDataFrameAfterSlice, testDataFrameAfterSlice, batchsize):
        readyForLearnTrainData = trainDataFrameAfterSlice.batch(batchsize)
        readyForLearnTestData = testDataFrameAfterSlice.batch(batchsize)

        return readyForLearnTrainData, readyForLearnTestData

    def learn(self, readyForLearnTrainData):
        model = tfdf.keras.RandomForestModel(num_trees=100, max_depth=12, min_examples=6)
        model.fit(readyForLearnTrainData)

        return model
