// Execute the exported fitted scikit-learn gradient boosting trees in the browser.
// sklearn's tree predictor converts each input feature to float32 before splitting.
export function predictConsumption(features,model){
  if(!model||!Array.isArray(model.trees)||!model.trees.length||!Number.isFinite(model.init_log)||!Number.isFinite(model.learning_rate))throw Error('Consumption model evidence is unavailable.');
  const values=model.feature_names.map(name=>{const value=features[name];if(typeof value!=='number'||!Number.isFinite(value))throw Error(`Supply a numeric ${name.replaceAll('_',' ')}.`);return Math.fround(value);});
  let score=model.init_log;
  for(const tree of model.trees){let node=0,guard=0;while(tree.children_left[node]!==-1){if(++guard>tree.children_left.length)throw Error('Consumption model tree is malformed.');const feature=tree.feature[node];node=values[feature]<=tree.threshold[node]?tree.children_left[node]:tree.children_right[node];}const leaf=tree.value[node];if(!Number.isFinite(leaf))throw Error('Consumption model leaf is malformed.');score+=model.learning_rate*leaf;}
  const annual=Math.expm1(score);if(!Number.isFinite(annual)||annual<=0)throw Error('Consumption prediction is outside the supported range.');return annual;
}

