from predictor import Predictor

if __name__ == "__main__":
    predictor = Predictor()

    predictor.load()

    print(predictor.next_day_prediction())
