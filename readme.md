
# Part1 Test the backtrader tools
## SimpleStrategy
first of all
we will create a policy for buying and selling after single fix percent indicator,which named test1.

we created a buy up sell down strategy and found that reward is about watching priod.

## Using indicators such as MACD
macd functions are in backtrader.indicators.

## Train a Strategy of CNN using Keras or Tensorflow
We use MACD indicator as input feature of 1-D CNN.

The outputs of CNN are the Q-Values of buying action, selling action and doing nothing.

we decide to create model first,and then use this shit model to decide what to do.
So we receive some states,action,reward