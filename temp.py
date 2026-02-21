import numpy as np
import xgboost as xgb

m = xgb.Booster()
m.load_model(r"models\solar_generation\models\xgboost_climatological_model_v2.json")

feature_names = ["latitude", "longitude", "abs_latitude", "month", "is_dry_season"]
X = np.array([[-1.2921, 36.8219, 1.2921, 2, 1]])
dm = xgb.DMatrix(X, feature_names=feature_names)
print(m.predict(dm))