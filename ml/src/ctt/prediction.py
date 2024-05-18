"""
This script does not contain any modular level code.
This is just for to give a reference that how the prediction pipeline works.
"""

if __name__ == "__main__":
    import joblib
    from sklearn.pipeline import Pipeline

    from src.configs import CTT_MODEL_PATH

    with CTT_MODEL_PATH.open("rb") as f:
        model: Pipeline = joblib.load(f)

    pred = model.predict(
        [
            "India russia pakistan china US",
            "campusx teaches machine learning krish naik",
            "mobile apple samsung",
        ],
    )
    print(pred)
