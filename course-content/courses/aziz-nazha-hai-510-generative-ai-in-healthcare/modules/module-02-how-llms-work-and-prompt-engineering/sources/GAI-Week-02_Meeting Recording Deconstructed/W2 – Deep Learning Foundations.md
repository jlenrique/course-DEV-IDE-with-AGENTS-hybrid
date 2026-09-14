# W2 – Deep Learning Foundations

[00:00:00] 


## Deep Learning Foundations

**Speaker 3:** So deep neural network, as we talked last lecture, you have... One of the thing you could think about machine learning and deep learning is that you have an input and you have an output, as we described it before, right?

So the input something that you bring in. Let me just... I'm sorry, I'm, I'm gonna mute. if somebody's not on mute, please mute yourself. so- The input layer and then you have the output layer. The output layer is something you're trying to predict. Now, we talked in the previous lecture about the algorithm in between.

Now, for deep learning, it was deep neural network, and then the idea is it's like the neuron. You have the body here, and you have the connection between those neurons. In our brain, th- those neurons fire up and, and then we get the answer, basically. So if we try to mathematically model that, you could take the input.

So let's say it's an image. You turn that into numbers, you put it in the first layer. This is, [00:01:00] and then there is through weight and bias, it's kind of go through the network and then give you the prediction and the output. Now, deep comes from how many layers are inside this neural network. So could be two, could be a thousand layers and, and this is how you get deep, scale of a deep neural network.

So this is what we call it, um, multi-layers percepton. Now this has evolved to become convolutional neural network, and convolutional neural network are good in image analysis, and I'll again quickly talk about how they work. And then recurrent neural network, and recurrent neural network used to be sort of the standard for text, and that was replaced now by the transformer architecture because this cannot be scaled.

If you're using a CT scan, for example, if you, if, if you're using AI [00:02:00] to read a CT scan image, most likely what you're doing, you are using, a deep, convolutional neural network to do that. So what are the building blocks for convolutional neural networks? So convolutional neural networks, can take the images and then turn it into pixels and then turn those pixels into numbers.

And then what it's gonna take, sort of take, take the edges, study the edges, kind of put them together to form the shape and objects. So how does that work? So one idea of this convolution is that if you take this matrix, again because algorithms typically don't know images, they don't... they do know numbers.

So you can take this And turn it into a matrix, and you have numbers here. And, and [00:03:00] then you have something called filter, and that filter is part of the image. And then it's sort of taking those numbers and kind of putting it together to come into a rep-representation. 'Cause what happen if you have a big image, now we're talking about thousands of pixels.

So you need to process this information quickly. The, the network need to process it quickly. So if you take each pixel and put it in here one by one, at one point the network is gonna run out of, of, uh, of, of, of, uh, ca-capacity. So what it's trying to do is to take those numbers and kind of do this convolutional layer, which taking that filter and reduce those number to, depending on the function, let's say max pooling.

So max pooling is, is pooling up the max number, and then move this filter one point and do it again and move it across [00:04:00] all this, image. So that will enable the convolutional neural network. If there is a small part of the image on the top, on the next image, it's on the bottom, it will enable it to actually detect that by moving the filter there.

So the idea, again, and, and I apologize if I... if this is still feel like it's a little bit, hard to kind of, uh, capture is, is that you're gonna take this image, you're gonna turn it into pixel, pixels into numbers, and you're gonna try to reduce those numbers with filters. At the end, you're gonna have a specific numbers, and those numbers will sort of shape the edges of the image and then give you the prediction based on those edges Now, with recurrent neural network, the idea here that you, you, you saw when we talked about the layers In a multilayer percepton, when you [00:05:00] move from layer to layer, there is no retention of memory, meaning the, the next layer is not gonna remember the previous layer.

In recurrent neural network, the idea is that the layers remember the previous layer and the layer before, so it has memory in it. This is why recurrent neural network has been good in text. Because in text, once you pass this text through the recurrent neural network, in order for the network to understand the sentence, it has to memorize the previous word, basically.

So this is how recurrent neural network evolved. So if you go to two thousand fifteen and fourteen and sixteen and seventeen, at that time, if you go on Google and type something, you, you see Google predicting the next word or doing the search for you. All of that was recurrent neural network. Now, one of the [00:06:00] challenges in that is if you have long text, it's really gonna be hard for the network to remember it.

And also, if you have like a big amount of text, it becomes very computationally expensive. Like it's-- was really hard to scale recurrent neural network. So the challenges in recurrent neural network at that time was forget long-range context. You would imagine that because again, depending on the number of layers in, in that neural network, it was slow because you gotta move word by word in each layer.

So for you to scale it on a big text, it was difficult and, and it was really hard to train too on the relationship between words. 'Cause the memory, it can remember that this word is related to the other word, but, but it cannot sometimes on a long context put those [00:07:00] words together. So it has difficulties.

This is why if you go back again in, in, in two thousands, even with the evolution of convolutional neural network, so imaging has been like having significant advances. Recurrent neural network, it wasn't like this aha moment, for, deep learning until transformers came. Now, transformers evolved from deep learning.

