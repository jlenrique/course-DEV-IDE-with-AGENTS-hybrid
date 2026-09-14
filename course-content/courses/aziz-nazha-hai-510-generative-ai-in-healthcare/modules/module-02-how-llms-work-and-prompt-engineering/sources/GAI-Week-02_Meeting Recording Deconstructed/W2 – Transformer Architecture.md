# W2 – Transformer Architecture

[00:00:00] 


## Transformer Architecture

**Speaker 3:** It's part of deep learning, and this is why I wanted to give you s-- a quick glimpse of how things evolve from multi- multilayer percepton to convolutional neural network, to recurrent neural network, and now the transformer architecture, which is the basic of large language models So in simple term Instead of reading word by word, Transformer look at the all words at once and learn how each related to each other.

So what we talked about, RNN, you're gonna pass the word by word into the layers. Here, there is a different architecture that works. Now, I promise you I'm not gonna give you any mathematical equations and those things. I think it's irrelevant, but we really need to understand how Transformer work because that will enable us to understand how large language models works.

And when [00:01:00] we understand how large language model works, we understand why they behave how they behave, meaning why they, sometimes hallucinate. So the process to, to get the Transformer to work is called tokenization and embedding. The second one is positional encoding, and the third one is self-attention.

In fact, the paper was published by Google in two thousand seventeen called Attention Is All You Need. That's the paper was the foundation for large language models. In other words, Google gave the world a free lunch for large language models, and they... At one point they were behind 'cause OpenAI took it over, and now they kind of came back.

But, but everything started with a paper coming out of-- came out of Google, and that paper was... The goal of that paper is to, improve translation. So Attention All You Need, [00:02:00] you probably hear a lot about this, paper. So let's unpack this. So tokenization. So the first step is that we talked about that computers and algorithms don't understand text.


## Tokenization & Embedding

**Speaker 3:** So what the model gonna do is gonna take this text, and it's gonna turn it into tokens and then map each token into a number See, now, there are... So the easiest way to think about it, well, yeah, each word is a token, but there are some words that can be two tokens. But, but the idea of tokens is that I'm gonna take each word, I'm gonna chop it, and I'm gonna give it a, a number.

This is why it's important now when we talk about tokens more, if you probably read the news about, we're running out of tokens because processing those tokens when we get to the large language models is... becomes what's [00:03:00] important for the model. So, so the first steps, we're gonna take the sentence, and we're gonna turn that sentence into tokens.

That's why we're gonna call it tokenization. Embedding, it's each token become a list of numbers, which is a vector that capture its meaning. So similar conce- concepts sit close together. So for example, myocardial, cardiac, and heart, these all have the same concept. They become a vector. So they sit next to each other.

They get numbers next to each other. Okay? So this is why embedding is very important. We, we'll see that. So now we have tokens. We put them together. They become a vector. And what we do, we build what we call it a vector database. We're gonna dump all of those words and their numbers in that big database.[00:04:00] 


## Positional Encoding

**Speaker 3:** The step after that, what we call it positional encoding Transformer is not gonna read words, they're gonna look at numbers. And also the position is important. So for example, if you come and say no history of cancer You say history of cancer. You see here just changing the position of the words change the entire meaning of the sentence.

So this is why the positional encoding take each token and kind of give it a certain position and based on that position becomes understanding the meaning of the word. 'Cause you could have again here the position of the same word in a different sentence, sentence mean different things. Step four is the self-attention.


## Self-Attention

**Speaker 3:** In the [00:05:00] sen-- self-attention is trying to understand in that sentence how the words are relevant to each other and this is sort of when we talked about attention is all you need. That's the mechanism in the transformer that enable it to understand the text. So another word to think about it is, is if I say, "Server, prepare my food," it's gonna be completely different meaning that than I crashed my server, and that's the whole thing of self-attention and the power of transformers.

So if you put that all together, this is how these models work. You're gonna have large amount of text. We're gonna take that text, we're gonna give it token. So token each word is, is one token. Then we're gonna take the words that have similar meaning, they kind of [00:06:00] cluster together. We're gonna embed them in a vector.

We're gonna take those vectors, we're gonna put them in a database. We're gonna call it vector database. And in that vector database, we're gonna add position. So that position will help the model understand each word position in the sentence might be different meaning, and it has the self-attention mechanism to it.

When we go to the large language models, we're gonna see how the large language models pu- pulling up those tokens and put them together. In other words, trying to predict the next word. But that's sort of the basics of, of how these models, work, and this is why this architecture is very scalable.

