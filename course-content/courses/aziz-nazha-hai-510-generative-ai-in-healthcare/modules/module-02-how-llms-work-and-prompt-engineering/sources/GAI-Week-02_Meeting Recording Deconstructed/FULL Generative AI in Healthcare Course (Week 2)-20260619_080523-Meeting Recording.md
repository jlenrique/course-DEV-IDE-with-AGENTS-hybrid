# Generative AI in Healthcare Course (Week 2)-20260619\_080523-Meeting Recording

**Speaker:** [00:00:00] Yes. Uh, 

**Speaker 2:** Sandra? A- and to be clear, it's not that we can't use other tools on Jefferson devices, it's that we can't use any Jefferson proprietary information, right? Yeah. Guidelines, tools, patient information. So- Correct. 

**Speaker 3:** Correct ... 

**Speaker 2:** so my follow-up to that was, like, if, if there was a de-identified data set, we can use that in Claude, correct?

**Speaker 3:** If it's not Jefferson related because 

**Speaker 2:** even- Even... So what if it's de-identified but it's Jefferson data? 

**Speaker 3:** You can't because, uh- 

**Speaker 2:** Cannot? ... 

**Speaker 3:** some of the... No, you cannot because Jeffers- some of the de-identified data through algorithm could be identified. 

**Speaker:** Hmm. 

**Speaker 3:** So that's anything Jefferson related, you are not allowed to use it on the other tools.

So, so this is [00:01:00] why it makes it, um... Now, uh, on the other tools, what I've been doing using, like, a mock data sets and those things, I can show you that, to be honest with you, Copilot, it- in its current version, if you, uh, if you get around that the user interface is annoying, it will get you 90% where you wanna go And the added capabilities that they have now, Cowork, probably will get you up there.

So, so that's what I wanna show you today in the, um, in the hands-on lab Uh, so, so and again, keep in mind that these tools are evolving and, uh, I feel like sometimes I'm a schizophrenic because you can ask me in the morning and I'll tell you something, and in the afternoon they have a new model came up [00:02:00] and it's like, "Ah, this is interesting."

Uh, it just evolving. So how do you, how do you do it? Well, keep evolving with it. That's what I keep telling people. The technology is moving so fast, so quickly, it's really hard to wrap your head around it. My hope with those educational seminars and courses i- is to get you the basics, the building foundation, and then you're gonna take that and build on the top of it.

So keep, keep, keep, keep playing with the tools over the weekend. Let's, let's put it this way. Uh, I think that's, that's the best way to think about it. And we... I mean, I showed you some of the tool we didn't even talk about, like text to image, image to video, um, and how much impact if you, if you're doing some like education or you're focusing on education, this stuff is, is also evolving very, very quickly.

All right. So let's, uh, start today. I have... I [00:03:00] tried to trim the slides, but I failed. Even Claude and, uh, and, uh, Copilot failed to trim them for me. So we have packed sort of agenda today. Let me, uh, let me share my screen

**Speaker:** Drawing goes. OK See

Okay, so this one is here 

**Speaker 3:** from the beginning. Okay. So, um, as you probably recall from the last, uh, week, uh, uh- Module. We, we talked about AI, we talked about how it's applied in healthcare, although I hope you had a chance to look at, at the slides on, on some of the examples. We talked [00:04:00] about machine learning, deep learning, generative AI, and the ev- evolution of terminology, generative AI, AGI, uh, uh, you know, super, uh, um, uh, uh, superhuman intelligence, all of this stuff we, we talked about last week.

Uh, and I hope we, we got to a point where we, we are able to distinguish between discriminative versus generative AI and, and get the idea. What I'm hoping to achieve in this module is to dive deep into The, um mechanics of generative AI. Now, for me to dive deep into that, I need to kind of give you a quick big background on deep learning, convolutional neural network, recurrent neural network, how that architecture evolved to become transformer.

Then we're [00:05:00] gonna talk about the transformer architecture. That's also what led to the development of the large language models. So really the main focus of this is to get to large language models. But in order for me to get there, we have to kind of review that. So I also recognize that this is not a machine learning course, and, uh, talking about just the basics of deep learning, that requires lectures.

So I'm gonna try to cruise through this. If you feel that this is too much, I apologize, but, um, I'm trying to get to large language models. We will have some conversations in the questions and answers. The other way, uh, I think might be useful to you is if you find there is a lot of terminologies here, my recommendation will be once you have time over the weekend or after hours or any time you have, [00:06:00] is to go back and say, "Okay," uh...

Actually, I've, I've, I've done that on Copilot or, or the tool. It's really good teacher. They are all of them good teachers, and they are really good in explaining topics, really good in giving you images to explain topics. So if, if you find convolutional neural network is like, "I didn't get it yet," go back to Copilot or the other tools and say, "Hey, explain convolutional neural network to me in, in very simple way."

And then work with it, and then it's kind of give you stuff and then, um, say, "Give me some citation. Give me..." So, so it's kind of evolve your, uh, understanding of that. So why do you need that? Well, I think it's, it's, it's important to know the basics because once you know the basics, the next steps becomes easier.

As we discussed at the beginning, the hope here to build the foundation, [00:07:00] and then you can build on the top of that foundation. 

**Speaker:** Right? 

**Speaker 3:** So deep neural network, as we talked last lecture, you have... One of the thing you could think about machine learning and deep learning is that you have an input and you have an output, as we described it before, right?

So the input something that you bring in. Let me just... I'm sorry, I'm, I'm gonna mute. Uh, if somebody's not on mute, please mute yourself. Uh, so- The input layer and then you have the output layer. The output layer is something you're trying to predict. Now, we talked in the previous lecture about the algorithm in between.

Now, for deep learning, it was deep neural network, and then the idea is it's like the neuron. You have the body here, and you have the connection between those neurons. In our brain, th- those neurons fire up and, and then we get the answer, basically. So if [00:08:00] we try to mathematically model that, you could take the input.

So let's say it's an image. You turn that into numbers, you put it in the first layer. This is, uh, uh... and then there is through weight and bias, it's kind of go through the network and then give you the prediction and the output. Now, deep comes from how many layers are inside this neural network. So could be two, could be a thousand layers and, and this is how you get deep, uh, scale of a deep neural network.

So this is what we call it, uh, um, um, multi-layers percepton. Now this has evolved to become convolutional neural network, and convolutional neural network are good in image analysis, and I'll again quickly talk about how they work. And then recurrent neural network, and recurrent neural network used to be sort of the standard for text, and [00:09:00] that was replaced now by the transformer architecture because this cannot be scaled.

If you're using a CT scan, for example, if you, if, if you're using AI to read a CT scan image, most likely what you're doing, you are using, uh, a deep, uh, convolutional neural network to do that. So what are the building blocks for convolutional neural networks? So convolutional neural networks, uh, can take the images and then turn it into pixels and then turn those pixels into numbers.

And then what it's gonna take, sort of take, take the edges, study the edges, kind of put them together to form the shape and objects. So how does that work? So one idea of this convolution is that if you take this matrix, [00:10:00] again because algorithms typically don't know images, they don't... they do know numbers.

So you can take this And turn it into a matrix, and you have numbers here. And, and then you have something called filter, and that filter is part of the image. And then it's sort of taking those numbers and kind of putting it together to come into a rep-representation. 'Cause what happen if you have a big image, now we're talking about thousands of pixels.

So you need to process this information quickly. The, the network need to process it quickly. So if you take each pixel and put it in here one by one, at one point the network is gonna run out of, of, uh, of, of, of, uh, ca-capacity. So what it's trying to do is to take those numbers and kind of do this convolutional layer, which [00:11:00] taking that filter and reduce those number to, depending on the function, let's say max pooling.

So max pooling is, is pooling up the max number, and then move this filter one point and do it again and move it across all this, uh, image. So that will enable the convolutional neural network. If there is a small part of the image on the top, on the next image, it's on the bottom, it will enable it to actually detect that by moving the filter there.

So the idea, again, and, and I apologize if I... if this is still feel like it's a little bit, um, uh, hard to kind of, uh, uh, capture is, is that you're gonna take this image, you're gonna turn it into pixel, pixels into numbers, and you're gonna try to reduce those numbers with filters. At the end, you're gonna have a specific numbers, and those numbers will [00:12:00] sort of shape the edges of the image and then give you the prediction based on those edges Now, with recurrent neural network, the idea here that you, you, you saw when we talked about the layers In a multilayer percepton, when you move from layer to layer, there is no retention of memory, meaning the, the next layer is not gonna remember the previous layer.

In recurrent neural network, the idea is that the layers remember the previous layer and the layer before, so it has memory in it. This is why recurrent neural network has been good in text. Because in text, once you pass this text through the recurrent neural network, in order for the network to understand the sentence, it has to memorize the previous word, basically.

So this is how recurrent neural network evolved. [00:13:00] So if you go to two thousand fifteen and fourteen and sixteen and seventeen, at that time, if you go on Google and type something, you, you, you see Google predicting the next word or doing the search for you. All of that was recurrent neural network. Now, one of the challenges in that is if you have long text, it's really gonna be hard for the network to remember it.

And also, if you have like a big amount of text, it becomes very computationally expensive. Like it's-- was really hard to scale recurrent neural network. So the challenges in recurrent neural network at that time was forget long-range context. You would imagine that because again, depending on the number of layers in, in that neural network, it was slow because you gotta move word by word in each layer.

[00:14:00] So for you to scale it on a big text, it was difficult and, and it was really hard to train too on the relationship between words. 'Cause the memory, it can remember that this word is related to the other word, but, but it cannot sometimes on a long context put those words together. So it has difficulties.

This is why if you go back again in, in, in, in two thousands, even with the evolution of convolutional neural network, so imaging has been like having significant advances. Recurrent neural network, it wasn't like this aha moment, uh, for, for, uh, deep learning until transformers came. Now, transformers evolved from deep learning.

It's part of deep learning, and this is why I wanted to give you s-- a quick glimpse of how things evolve from multi- multilayer percepton to [00:15:00] convolutional neural network, to recurrent neural network, and now the transformer architecture, which is the basic of large language models So in simple term Instead of reading word by word, Transformer look at the all words at once and learn how each related to each other.

So what we talked about, RNN, you're gonna pass the word by word into the layers. Here, there is a different architecture that works. Now, I promise you I'm not gonna give you any mathematical equations and those things. I think it's irrelevant, but we really need to understand how Transformer work because that will enable us to understand how large language models works.

And when we understand how large language model works, we understand why they behave how [00:16:00] they behave, meaning why they, uh, sometimes hallucinate. So the process to, to get the Transformer to work is called tokenization and embedding. The second one is positional encoding, and the third one is self-attention.

In fact, the paper was published by Google in two thousand seventeen called Attention Is All You Need. That's the paper was the foundation for large language models. In other words, Google gave the world a free lunch for large language models, and they... At one point they were behind 'cause OpenAI took it over, and now they kind of came back.

But, but everything started with a paper coming out of-- came out of Google, and that paper was... The goal of that paper is to, uh, improve translation. So Attention All You Need, you, you probably hear a lot about this, uh, paper. So let's unpack this. So [00:17:00] tokenization. So the first step is that we talked about that computers and algorithms don't understand text.

So what the model gonna do is gonna take this text, and it's gonna turn it into tokens so... and then map each token into a number See, now, there are... So the easiest way to think about it, well, yeah, um, each word is a token, but there are some words that can be two tokens. But, but the idea of tokens is that I'm gonna take each word, I'm gonna chop it, and I'm gonna give it a, a, a number.

This is why it's important now when we talk about tokens more, if you probably read the news about, like, we're running out of tokens because processing those tokens when we get to the large language models is... becomes what's [00:18:00] important for the model. So, so the first steps, we're gonna take the sentence, and we're gonna turn that sentence into tokens.

That's why we're gonna call it tokenization. Embedding, it's each token become a list of numbers, which is a vector that capture its meaning. So similar conce- concepts sit close together. So for example, myocardial, cardiac, and heart, these all have the same concept. They become a vector. So they sit next to each other.

They get numbers next to each other. Okay? So this is why embedding is very important. We, we'll see that. So now we have tokens. We put them together. They become a vector. And what we do, we build what we call it a vector database. We're gonna dump all of those words and their numbers in that big database.[00:19:00] 

The step after that, what we call it positional encoding Transformer is not gonna read words, they're gonna look at numbers. And also the position is important. So for example, if you come and say no history of cancer You say history of cancer. You see here just changing the position of the words change the entire meaning of the sentence.

So this is why the positional encoding take each token and kind of give it a certain position and based on that position becomes understanding the meaning of the word. 'Cause you could have again here the position of the same word in a different sentence, sentence mean different things. Step [00:20:00] four is the self-attention.

In the sen-- self-attention is trying to understand in that sentence how the words are relevant to each other and this is sort of when we talked about attention is all you need. That's the mechanism in the transformer that enable it to understand the text. So another word to think about it is, is, is if I say, "Server, prepare my food," it's gonna be completely different meaning that than I crashed my server, and that's the whole thing of self-attention and the power of transformers.

So if you put that all together, this is how these models work. You're gonna have large amount of text. We're gonna take that text, we're gonna give it token. So token each word is, [00:21:00] is one token. Then we're gonna take the words that have similar meaning, they kind of cluster together. We're gonna embed them in a vector.

We're gonna take those vectors, we're gonna put them in a database. We're gonna call it vector database. And in that vector database, we're gonna add position. So that position will help the model understand each word position in the sentence might be different meaning, and it has the self-attention mechanism to it.

When we go to the large language models, we're gonna see how the large language models pu- pulling up those tokens and put them together. In other words, trying to predict the next word. But that's sort of the basics of, of how these models, uh, work, and this is why this architecture is very scalable.

Because now instead of running word by word through each [00:22:00] layer, we go to the vector database, and we pull up all of those tokens and, and vectors basically. So it becomes easier to process the text. That- Development led to the development of large language models or LLMs. And what a large language model is, it simply is an AI program designed to process and generate text.

So it's a language model that mimic human language. Where, where large come from? This trains on trillions of tokens. It has pil- billions of parameters and pre-tuned and fine-tuned on tasks. So what OpenAI did back in the days in two thousand seventeen, eighteen, and nineteen, they went to the internet and they took all the text in the internet.[00:23:00] 

So imagine now you have the internet text. They turn it into tokens, and then they start build this transformers model but, but, but maybe more like, uh, in a more scalable way. So they have billions of parameters of these models. I mean, I remember when, when, when... So you have GPT 1, GPT 2. GPT 3.5, this is the large language models from OpenAI, that's the first time ChatGPT came in.

So ChatGPT is the user interface. It's how you look at it, basically. And in the, the first time when, um, ChatGPT came out, that was like 3.5. So it's the model that evolved from GPT 1 to 2 to... And, and they say 3.5 at that time is trained on like a-- I forgot the exact number, but we're talking about, uh, billions of parameters.

Then 4 was trained on trillions, and then they stopped saying how much data is trained on it. But, but that's what happened, and this is why [00:24:00] if you go back at that time, the New York Times and other publishers start suing OpenAI because they took their content without their permission to train these models.

So we have two types of models. We have general-purpose model, pre-trained on massive amount of data for general purpose. So everything you use in Copilot, Claude, and OpenAI, these are general-purpose models. So when we talked last time, when we showed the tool, and we're gonna talk again when we show Copilot.

Copilot is the user interface. It's not the large language model. The large language model, I can go up and choose. GPT 5.5, that's the most recent model from OpenAI. Opus 4.8, that's the recent model from Claude. [00:25:00] You probably heard in the news there was a new model called Fable from Claude that was stopped now.

There's a dis- dispute with the government among the model and all of the stuff. Let's park that on the side, but that's the name of the model. There are Chinese models that are out there: DeepSeek, Kiwi, Owen. So these are general-purpose model. Now, what you can do, there are two types of model. There are open source models, and there are foundation or frontier models.

Frontier models like GPT 5.5, Claude, and other models, those ones you cannot download. They're not open to the public. You have to pay for it. Where there are open source model, the open source model is where you take the model, you can [00:26:00] download it, not all of them, but the, the smaller one, on your laptop and use it for free.

So those typically are the Chinese models DeepSeek, Kiwi. So that's what we call it open source models. Fine-tune models. You can take an open source model, train it on your data, and that becomes a fine-tuned model. So meaning that you can focus the expertise of that model on your own data. In my experience, I can tell you fine-tuning the models used to be something interesting.

Any general purpose models will outperform fine-tune models. It just waste of time now because the race and, and the amount of complexity of these models, the amount of, of, of, uh, e-evolution of these models, it's, it's, it's [00:27:00] insane. And fine-tuning the models takes time, effort, and energy, and compute, and costs money.

We'll talk about reinforcement learning from a human feedback in a second. Sandra? 

**Speaker 2:** Is, is UpToDate a fine-tuned model? 

**Speaker 3:** Yes. Just to get context. So I, I think so. I think so. I, I shouldn't say yes. So the idea there is that it's trained on UpToDate models. Now, what you also can do instead of training it on it...

So this is why I'm not one hundred percent sure. You can take general purpose model and point it to the context on UpToDate instead of training it on that context, and that pointing- In my experience and re-research that I have done, it's actually typically yield better result compared to fine-tuned models.[00:28:00] 

So that's what open evidence has basically, um- 

**Speaker 2:** Can, can I ask a follow-up? 

**Speaker 3:** Yeah, yeah. Sorry. Please. 

**Speaker 2:** Sorry. So, so when you say point it, you're talk... I think you're talking about prompts, which you said you're gonna cover later. But is it basically going into one of the general-purpose models and say, "Use up-to-date and other sources to explain this or figure out this question for me?"

Is that, is that what you mean? 

**Speaker 3:** Right. So, so think about it this way. So let's say you have ten review articles about a disease. You take those review articles and put them in a folder. And what you can do, you can take large language model and say... So, so let's, let's process this. How's that, how's that gonna work, right?

You're gonna take those PDFs which has text, right? You're gonna turn, turn [00:29:00] that text into tokens. You're gonna put it, do embedding, and you're gonna put it on a vector database. Yeah? So all of this becomes a vector database. Then you're gonna point the large language models to that vector database and say, "If I ask you any questions, you just answered from that vector database."

Right? So this is how it works. And then what you can do, you can engineer it to say, "If the answer is not in that vector database, don't make it up." Or, "If the answer is not there, go search the internet and make it up." And this is how you kind of build that workflow.

Where fine-tuning, you're gonna take that ten documents and you're gonna come up with the questions and answer, and then you're gonna go and then tell the model, "If I ask you this question, this is the answer. If I ask you the question, this is the answer." And then retrain, change the parameters of the models, [00:30:00] and that becomes fine-tuned model.

This is why it takes time, energy, because you have to label the data and you have to train it, and it takes a lot of time and effort and money. And honestly, in my experience, the one that you point the large language model to, it, it outperformed the fine-tuning. Does that make sense?

No 

**Speaker 4:** No, totally it does. Thank you. 

**Speaker 3:** Perfect. It's the same thing, by the way, if you think about it from EMR, from, from, like, Epic. Uh, you have all this data in Epic, and I now can point, let's say, GPT-4 or 5.5 to that Epic data and extract the information from it. So, so that's when, uh, it works. This is just to show you the evolution of large language models.

As we discussed, transformers came out in two thousand and seventeen. They're like, uh, BERT and [00:31:00] GPT-2 in the '18 and '19 were, like, hot until GPT-3 came, and you can see billions of parameters at that time. And then the release of ChatGPT, which was GPT-3.5, and now we have all of these models that evolve and continue to evolve.

And there are, like, uh, websites where they can rank them. And I can tell you what's interesting about this, that some of these models, they rank high in physics, in, in math and software engineering, has nothing to do with, with healthcare questions. And I still think we need to develop better evaluation of these models in healthcare, and that's something of the research that I, I'm, I'm very interested in and, and we're, we're working on, uh, too.

All right. So how these large language models work. So we talked about the transformers. We talked about the positioning, encoding, the vector database. What the [00:32:00] model actually does here is trying to give probability. So, so once you ask a question, the large language model's gonna go to that vector database we described.

It's gonna start pulling token by token, right? Now, as it's pulling those tokens, it's gonna put the token and gonna predict the probability of the next word based on the word before or the token before. So, for example, if you put a prompt, "The patient was prescribed five hundred milligrams of," it's gonna come back and say, "Okay, it could be amoxicillin, acetaminophen, metformin."

So it's gonna have a probability of words and then gonna predict that the highest probability is gonna be amoxicillin. So think about that. This is how these models work. So as it's putting the text out, it's kind of predicting the next text. So this is open the whole question, are these models intelligent [00:33:00] or just predicting the next text?

So that's number one, though. It sounds intelligent because it's putting words together, and it used to be back in the days that it, like, anytime, like, on the GPT-3.5 and 4, it's like, it's like putting a lot of words. It's, like, too wordy. Now they come around and, and, and actually improve that. But this is also why these models hallucinate.

Why? Well, if it have the next word and the probability of that word is wrong, predicting it wrong, it looks to you hallucination. So for example, if it comes and say the patient was prescribed five hundred milligram of, instead of saying amoxicillin, said metformin. Metformin has five hundred milligram too.

To you, oh, the model hallucinate because it's pre-- I wasn't talking about metformin, I was talking about amoxicillin. To the model, it did not. It could be metformin, it could be [00:34:00] amoxicillin. This is why hallucination is interesting. So hallucination dropped dramatically on recent models, but cannot be zero because there was actually a big paper, big nice paper coming out of OpenAI.

There are some stuff also we as humans don't a-agree on. So how we... And, and when we see it in the model, we say this is a hallucination, this is incorrect. Well, but if we don't agree on something, how is that is incorrect? So now does the model make mistakes? Yes. In fact, in healthcare, we have research showing on a complex oncological questions, these models have a-- even the best ones have about thirty, forty percent hallucination rate, uh, making up stuff that's not in the guidelines, uh, not sticking up with the guidelines.

Now you know why, because it's predicting the next word, and the next word is wrong or putting like [00:35:00] treatment together, and then that treatment doesn't exist. This is why traditionally these models were not good in references. Think about it. So I'm gonna pull up token by token. So I can come up with a reference for Aziz Nazha that doesn't exist because if I predict the next author wrong, the whole reference is wrong.

And they used to be terrible at this. Now they improve that by, uh, they sort of engineering a long context of some of those references. So, so now I'm hoping that you sort of understand to, to a deeper level why these models-- how they work, but why also hallucinate. So to wrap this up Models don't understand text, they understand numbers.

They're gonna take the text, they're gonna turn it into tokens. So now when you hear the token world, wo-- uh, token war, [00:36:00] you hear, oh, for example, Claude Opus four, uh, four point eight, it cost... I forgot the exact number, so don't quote me to it, but let's say it cost about fifteen dollars for one million token in, and then how many tokens out.

So there's cost for token in and for token out. So if you go to any, um, like now you see for example, GPT 5, uh, what is it? Mini, uh, like, uh, four point o mini, it costs twenty-seven cents for token in, uh, for one million token in and one million token out. This is why if you go now to ChatGPT, for example, the free version, it will start using five point five, and then after two it'll tell you, "Eh, we're gonna put you on a, in a low model."

Why? Because it's expensive to run all of those tokens for [00:37:00] free. This is why if you use paid version of Claude, for example, and try to do some work, it kick you out. You run out of token because now you're ex-- you're, you're too expensive because token in, token out costs money and compute. This is why, if you hear in the news, we need a lot of big data centers and each state's trying to big, to build those big data centers because we start running out of tokens.

Because we need a lot of tokens to, to, um, to operate all of these models, because now we're gonna have everybody, uh, uh, um, lose their jobs and we need tokens. Asians gonna rule out the world, and we need all of these tokens. This is why last year, six hundred billion dollars committed to infrastructure to build data centers that enable us to handle those tokens.

So again, you start [00:38:00] with the token, you embed them, put them in a vector database, and then we're gonna predict the next token

Right, this is... A quick important thing sometimes get missed. This is one of the most important thing that OpenAI did with large language models. So if you think about large language models, GPT-1, GPT-2, and the attempt from other companies before. They have a lot of attempts to put those chatbot where you ask it a questions and answer it to you.

The challenge at that time was if you go-- So if you go on a GPT-1, this is the first model that came out, and say, "Okay, well, I get I... You..." Actually, they made it open source, so you can download it on your laptop. And at that time you, you should go, you can go and say, "Well, um, give me five steps to build a nuclear bomb."

And the model will be like, "Oh, these are the five steps to build nuclear bomb." Why? [00:39:00] Because it has the data in it, so there is no guardrails. So they start seeing, for example in previous attempt, if you curse at the model, the model will curse back at you. Now, you don't want that to be happening in the public, so you have to put guardrails But putting guardrails on like millions of questions is not an easy task.

So what they did, and this is-- this step is very important, get missed a lot. So they did something called reinforcement learning from human feedback. So what they did, they took the questions and answers for like difficult questions, OpenAI did. They collected the response. They have a human re- human review it one by one, rank it or flag it.

This is good, this is bad. These humans were actually in, in Kenya, in Africa because they pay them like very minimal amount of money 'cause this has cost a lot of [00:40:00] money. 'Cause it's not one, two, three response. We're talking about hundred thousands responses we need to, to, um, to, uh, code. And then they build this reinforcement learning, and reinforcement learning meaning y- you can't also...

I mean, just one by one build that. But what they did, they, they took the, um, responses and then have the model through reinforcement say, "Yeah, if something similar come up, you know, you should block it or put the guardrails on it." This is why if you go on ChatGPT today, which you please don't, but if you say, "Hey, help me build a nuclear bomb."

It'll say, "No, I'm not gonna help you to do that." Or if you say, "Oh, I wanna cheat in, in Sony game. Help me cheat." It's gonna flag you. Say, "No, no, um, uh, I can't. I'm a large language model, I can't help you do bad things." So these are the guardrails that enable the model to be technically safe. What we will learn [00:41:00] next week is how do we get around that.

Something called jailbreaking, which is how do you get the model to do something that it's not supposed to do by indirectly asking the question? And this is why, you know, some of the report, this is why they shut down Fable because part of it is, is that, um, it's kind of degraded you. I, I don't wanna go there because there are two sides to of that story.

But, but, um, some people were able to break that model, and by breaking that model you can do bad things. So we have to be careful with, with these models, especially in healthcare. If you put a guardrail on a model, for example, not to accept PHI There's a way around it. That's a problem for us in healthcare, and that's what we will learn next week.

But, but keep this in mind. Reinforcement learning with the human feedback was very [00:42:00] important for the success of ChatGPT because that's enabled the model to be safe when you ask it very difficult questions or a question that it shouldn't answer it for you

All right, prompt engineering. I'm gonna pause for a minute. Any questions? We'll go through prompt engineering, and then, uh, we will take a break, ten minutes, and we'll come back, and we'll talk about, uh, uh, how do we-- Like, we'll, we'll, we'll go on, on, um, Copilot, and then we, we all gonna start practicing prompt engineering together.

Any questions before we talk about prompt engineering?

All right? So prompt engineering is if you think about the model is fixed, prompt engineering is how do you steer the model. So [00:43:00] another where-- way we talked about large language models, we talked about intelligence. Are these intelligent model not? But there's a certain way we need to talk, uh, to these models to get the best out of it.

So th- this is how... So prompt engineering is how do we talk to these models to get the best and most out of it. 'Cause it's not similar to talking to human. There are specific way to talk, and that's what we're gonna learn here. There are so many ways, so many lectures about prompt engineering. I'll give you my personal experience.

Not to say this is the right or wrong. It's a starting point. Play with it. Certainly, my prompt engineering has evolved too, I can tell you that, over the years. Um, uh, so play with it. Think about it. Choose the best for you. Go back to the model. Ask it, "How do I improve my prompts and [00:44:00] those things?" But, but this is how I think about it, not to say that this is the, the best or the only way to think about, uh, prompt engineering.

There are rules. General prompt will give you general answer. Th- this is, this is important. Specific prompt give you specific answer. So if you go and write an email and say, "Rewrite this email," get um okay answer. If you give it a context and say, "Look, my boss sent me this email. I don't know how to reply to that email.

I wanna be polite. I wanna be, uh, correct, and how do I frame this?" Now you're getting better email. So general prompt will give you general answer. Specific prompt will give you specific answer. One of the challenges of these models, obviously, in ChatGPT and, and Copilot and other, no matter what you ask, it's gonna answer you.

And I used to go to these classes and say, "If you, if you tell [00:45:00] ChatGPT... If you get ChatGPT to tell you, 'I don't know,' I'll give you a hundred bucks." So of course you get a smart person going to ChatGPT and say, "Hey, tell me I don't know." And then ChatGPT will say, "I don't know." And then they send it to me and say, "Hey, give me a hundred dollars."

That's not what I mean. No matter what you ask, it's gonna answer you, and the answer is very plausible. And for somebody who doesn't know the topic, it's very plausible. And I'm gonna be honest with you, the more you work with these models, depending on the model, ChatGPT, for example, is very manipulative.

It look at your history. It look at your, like, memories, try to tailor the answer to you. To-- meaning it's not gonna confront you, and if you confront the model, it's gonna say, "Oh, hey, I'm sorry." It's- The whole idea is to try to keep you on the platform. So keep that in mind too. Um, garbage in, garbage out.

That's i-i-in, in, in, in, in [00:46:00] any machine learning, and this is very important. It's an iterative process, so you might not get the best out of the first prompt. Work with the model. Ask it. So s- it's multiple time. It might not be the best, and I've had this conversation situation with people where they go on ChatGPT, they ask it something, it's like, "Ah, it's, it's done.

I'm not gonna go back again," and they never use the system again. No, no, no. Learn prompt engineering. Learn how to use it. Keep in mind it's an iterative process. Okay. So each prompt has essentials to it, and again, this has evolved even for me. But in each prompt you need So I started wiring my brain that way You-- As you're working with these models, you, you will start prompting, you will get to that.

So the first thing is the [00:47:00] role, and you give it a role. So if you're trying to ask it a question and say, you know, "You are a physician at a healthcare system," or, "You are a patient," you're gonna get different answer. "You are a software engineer trying to build an app." Give it that persona and role. That's extremely important.

The most important one, obviously, it's a task. So you go to Copilot or other tools to ask it to do something for you. And task could be simple, just answer this question. Or it could be complex. Take this attached file, extract the information, summarize it in th- in, in, in a paragraph, and then in a three bullet points.

See, that's more like a complex tasks. Or you could go make it more complex. Go to my Expedia, search it, find me flights that going to Rome, that, uh, going in the [00:48:00] morning on Saturday, organize these in a, in a table, give me the price of these slides-- uh, the flights. So you, you can see there are tasks that are simple, there are tasks that are complex that you can ask it.

Very important, give it a context. Set up the stage for it. So give it the background. So if you are a physician, if you go and ask, "Well, give me differential diagnosis of low hemoglobin," eh. If you come and say, "Well, you are a physicians working in the hospital. Have eighty-year-old showing up with CBC, this and that."

Now you give it better-- that context, it's gonna give you a better answer. I can guarantee you that. Give it a context. Then think about the format that you want the answer to be back. This is also important because if, if, if you want it to, to give you a paragraph and it give you a document, or if you want it to give [00:49:00] you a, a bullet point, tell it.

Give it an example and tell it. Specify how the output gonna be. I want slide deck. I want PDF. I want an app. I want this design for the app. So don't go and say, "Build this website for me." Well, give me the design, give me some information, then give me some context. It's important for us is to set sometimes guardrails depending on what you're asking too.

Like, uh, don't, um... For example, if you're doing a, a, a, a search, if you're asking it to give you a treatment, say, "Cite the source." 'Cause now ChatGPT, for example, it's not gonna cite it, but you could force it to cite it. Say, "Where did you get your information from? So if you give me a treatment for this patient, cite the- The source, and it will cite it for you.

That's how we make these models better for us in healthcare. Set up the [00:50:00] guardrails. You need all of those, uh, uh, to get a better prompt. And then as you're working with a prompt, again, you start with the role, give it a task, think about the format, try to give it a context. And sometimes, depending on what you're doing, you need to give it a guardrail So these are some prompts.

Act as a nurse educator. This is the role. Explain how to use an insulin pen to a patient with low health literacy in six short steps at sixth-grade level. Avoid medical jargon. So here you see the task, and the task is multiple. Uh, you probably need to give it a better context, meaning, you know, you are a nurse educator, you are working with patients, uh, um, with diabetes pa-- with diabetic patients in a clinic, and you want to provide [00:51:00] educations for them.

Even more context. Avoid medical jargon. You know, setting up some guardrails. Summarize the discharge note for primary care physicians in five bullet point. This is not, not the perfect prompt, by the way. This is why we, what we're gonna learn at the, at the, uh, at the next time. So each one start with a role.

You are a physician. You are a software engineer. Give it a clear task, even give it step-by-step. Give it a context. Think about how do you want it to answer to you. Go back to the first principle. General prompt, general answer. Specific prompt, specific answers. All right. I guess that's it. Any questions about prompt engineering or what we learned so far?

Sandra? 

**Speaker 2:** Yeah. Uh, I... This week actually, I put-- took a old slide [00:52:00] deck and put it into ChatGPT and gave it the context of who the learners were, how many, um, and asked it to update it with, you know, and gave the references. And it, it, it was unable to take the images from my previous slide, slide deck and put it into the new slide deck.

Yeah. Um, what... How should I... How can I make it do that? 

**Speaker 3:** ChatGPT is not good in that, so it's not gonna do it for you. Um, again, if it's Jefferson stuff, you need to do it on Copilot. But it's not Jefferson stuff, uh, uh, Claude will be your best bet. 

**Speaker 2:** And, and Claude would do that. It would take the photographs that I have and put it into a new slide deck.

Okay. 

**Speaker 3:** But tell it- 

**Speaker 2:** I've not 

**Speaker 3:** used Claude ... don't change the style. Don't change. Add the same images. Sneak in in a slide there, so it will do it for you. Um, Copilot could do a good job because it's connected to PowerPoint, [00:53:00] and it could extrapolate that. Uh, but for building slides, the best one is, uh, Claude.

ChatGPT is not good. Thanks.

**Speaker:** All right. I guess we all looking forward for a 10 minutes break. Let's do that, and then we'll come back and, and, and do some exercises of prompt engineering[00:54:00] [00:55:00] [00:56:00] [00:57:00] [00:58:00] [00:59:00] [01:00:00] [01:01:00] [01:02:00] [01:03:00] [01:04:00] 

**Speaker 3:** Okay. Um, let's get back. Um, so maybe we can talk a little bit about Copilot, show you, uh, some of the capabilities. We can practice some prompt engineering, and hopefully you, you go and enjoy your Friday and, and early weekend. Uh, so, so that's the goal [01:05:00] here. Okay. So, um, the tool that we needed to talk about was Copilot because that's the one that we all needs to use.

So there are so many ways you can get to Copilot, but the easiest one is to go copilot.microsoft.com. Now you get to this always, this sort of, uh, site, and I wanted to, to show you because it's important. This is what get you to your personal Copilot. This one will get you to your work Copilot. You wanna be on your work Copilot if you're trying to use, uh, some of, of, of, uh, Jefferson data.

So if you click on Word Copilot, you, you get here. It's how it looks. Now, the look is, is, is similar to what we talked about in the other, uh, tools. Uh, you-- here you kind of talk to Copilot. You can upload and add content, [01:06:00] upload from images, or you can share from your SharePoint or Drive. Um, you can connect it to Word, Excel, and PowerPoint.

That's one of the good thing about Copilot. And then, um, has some other capabilities in terms of agents. Now, we talked about agents, and we want you to build an agent by the end of this course. So this is where we wanna focus our attention to Copilot too. Um, there are two

Shouldn't say types of Copilot, but, but there are two things of Copilot. One is the free version. The free version has less capa- capabilities and cannot integrate with, um, with Microsoft tools. The one I have here is the three hundred sixty-five Copilot. [01:07:00] That will integrate with my emails, integrate with my slides, integrate with PowerPoint.

That one is a license you have to request. So you have to send a request from IT, and IT will give you the license. We pay about thirty dollars per license. Uh, so it's not a cheap license, too, but, but you could request that license, and IT will give you that license. This is where, again, we talked about the model.

On Copilot, you could use the OpenAI models, and you could use Opus, which is a Claude model It has a quick response and think deeper. Quick response or auto. So auto, quick response, and think deeper. So auto, it will decide depending on your question whether it needs to think deeper or not. The think deeper one is sort of a think before it does something.

Um, and that's if you have like a complex task or you want it to do a different thing, [01:08:00] put it on think deeper, you will find it better. Takes longer for the answer, but you will find hopefully better answer. So, uh, all right. So I am an AI educator. I am teaching a class about prompt engineering in healthcare.

Give me ten-

Uh, use cases that I can 

**Speaker:** have the class work on to improve their Skills with prompt engineering. Give me the cases

And key to solve it [01:09:00] and one by one and one I ask you about Prompt, you will provide

Provide perfect one. Be academic. Be creative. All right. Shout it out. I am an AI educator. What is that?

Perfect. I'm teaching a class 

**Speaker 3:** about prompt engineering in healthcare 

**Speaker 5:** Context 

**Speaker 3:** Yeah. Give me 10 use cases that I can share with the class, uh, share, uh... Can have the class work on to improve their skills with prompt engineering. Give [01:10:00] me the cases, key to solve one by one, and when I ask you about the prompt, give me the perfect prompt.

**Speaker 5:** Task. Task. Task and format. Yeah. 

**Speaker 3:** Yeah. Perfect. And 

**Speaker 5:** guardrails. 

**Speaker 3:** Be academic, be creative. 

**Speaker 6:** Guardrails. 

**Speaker 5:** Guardrails, yep. 

**Speaker 3:** Yeah. Uh, not... So this one we didn't talk about in the slide. So- 

**Speaker 5:** Yeah ... 

**Speaker 3:** uh, for, so I find, uh, what we call it the, uh, tone. So we didn't talk about it in the slides. Um, sometimes it's important. So tone, you're setting up the tone.

So if you're working on a academic paper, be academic, be accurate. If you want it to be funny, so for example, I can say it's, and it's pretty funny, so be funny. So it would give you funny use cases. So tone is, is important. I didn't put it there. Uh, now guardrails will [01:11:00] be like, "Hey, give me only healthcare 

**Speaker:** use cases."

All right

**Speaker 3:** So now it's gonna give me the scenario, and now you guys gonna

Prompted. We'll give you five minutes to prompt it, and then somebody will give us the prompt, and then we, we will critique your prompt. And, um, we will actually put your prompt in the chat. We will give it to, uh, Copilot, and we'll ask Copilot to score your, your prompt. Okay? All right. So a resident pastes the three pages HPI into ChatGPT, which they're not supposed to, and says, "Summarize please."

The challenge: output is vague, misses critical clinical [01:12:00] details So you are a physician or a resident, you have a PHI or HPI. How would you restructure that with Copilot, not ChatGPT? What it will be the perfect prompt

**Speaker:** Give you a few minutes

Have a good representations of physicians on, on this course, so you should get perfect prompt[01:13:00] 

**Speaker 4:** Are we supposed to post this in the chat, or what do you want 

**Speaker:** us to do? 

**Speaker 4:** Yeah. 

**Speaker:** Yeah, let's post it in the chat, and then we will see what you guys posted, and then we will, uh

All right. So Manisha creates structured history keeping the key avoid repetition. What is missing here? [01:14:00] 

**Speaker 4:** The role? 

**Speaker:** Yeah. Yeah. 

**Speaker 3:** All right. Sandra, act as attending physicians, and please create a summary of HPI preserving all relevant clinical details into the paragraph. So, so yeah, you can say that you act or you are an attending physicians.

What's missing here?

Nothing? Pairing Week 

**Speaker 6:** Give you context? 

**Speaker 3:** Context, yes. Give it more context, right? So, um, you are a physician working in a healthcare system. You are writing a PHI or HPI for the patients in the clinic, and you want to have, uh, full [01:15:00] details and make it brief. And then give it the task. Take the summary or take this text, rewrite it in, in this format.

Mm-hmm. Right? And then give it the tone. Be brief, be accurate- All right. You're a physician in primary care. Help me create a summary of an PHI of a patient. Be concise and straightforward. That's good, right? Be concise and straightforward. Only include pertinent issues. Prefer bullets. Okay, so getting there.

All right. What is missing here?

All right. Maybe I shouldn't score your prompt. I will ask... Gonna pick one, okay? I'll ask Copilot to do that for you so I'm not the bad guy. 

**Speaker:** Oh, 

**Speaker 3:** you have to[01:16:00] 

pick mine? I know somebody gonna say, "Why mine? Why me?" So score this prompt

And see, my prompt is bad too. Score this prompt. What does that mean, right? But let's see.

Not bad, not bad. 7.5 

**Speaker:** out of 10 Junior 

**Speaker 3:** to intermediate Yeah. Good junior to intermediate prompt. All right. Physician, so you define the role, the task, style guidance. Here's what you're missing. No instruction to preserve all key clinical facts, no structural definition, no hallucination protection. Mm-hmm. 

**Speaker:** Ah.

**Speaker 3:** We didn't put some guardrails, yeah?

No audience 

**Speaker 2:** So how do you do the hallucination protection here? 

**Speaker 3:** So try to be accurate. Don't make up facts. 

**Speaker 5:** Yeah. 

**Speaker 3:** This is how you tell it. [01:17:00] Be accurate. Be- Don't 

**Speaker 2:** make up facts Well, you pretty much have to do that for everyone, everyone then if 

**Speaker 5:** you're gonna not give it- You do. You have to tell it not to improvise.

Only, only- 

**Speaker 3:** Yeah ... 

**Speaker 5:** give me what you have for me. Don't make up 

**Speaker 3:** stuff. 

**Speaker 5:** Yeah, don't make up stuff. Yeah, yeah. Tell it. That's what my son says he does. No, please. He tells it, "Don't make anything up. Show me, show me citations." 

**Speaker 3:** That's great. Yeah. Exactly. All right, so let's, um- 

**Speaker 5:** Do 

**Speaker 3:** not embed ... give it a second. 

**Speaker 5:** Yeah. 

**Speaker 3:** Let's do, do this one.

Actually, this is the other thing, and that's what I do all the time. So how do... Learn with it. Ask it, "How do I pr- uh, uh, write," or, "How, uh, how do I prevent hallowi- hallu- cinination? What should..." No, see? I don't e- know how to speak it. So what should I- Add to my pro- prompt to [01:18:00] ask it to avoid hallucinations

Great questions Use only the information provided. Do not add, infer, or assume any details that are not explicitly stated. If information is incomplete, reflect that rather than filling in 

**Speaker 5:** gaps. 

**Speaker 3:** Even better, use only the information provided. Do not add, infer, or assume any additional details. Do not generate symptoms, diagnosis, timeline, blah, blah, blah.

If any information is unclear or missing, state it explicitly rather than guessing it. 

**Speaker:** Mm. All 

**Speaker 3:** right? Okay. Now, the stakes are higher. Let's go to the second one. Um- 

**Speaker 5:** I do like the titles it's coming up with. It is being funny. It's [01:19:00] amusing. 

**Speaker 3:** Exactly. It's exactly. That's why you need to set up the tone, right?

Hey, if I said be serious, uh, it wouldn't be like this. Okay, discharge summary disaster. Write this discharge summary. 

**Speaker 5:** Yeah, write some novel 

**Speaker 3:** Yes. So skill, how does an agent prevent, well, prevention. Let's see. Have a few minutes. Paste your in the chat, and then we will score randomly

**Speaker 7:** And Aziz, we have, um, a hand up from Darren 

**Speaker 3:** Oh, I'm sorry. I don't see... Darren, yeah. Sorry. 

**Speaker 8:** Yeah, Aziz, what I was gonna say, and, and I just... I found out, I know, like, with Google Gemini, you can kind of put, like, these parameters in so you don't have to type it out every time. Yes. Like, you can create, like, a profile.

So I did see that you can do that in Copilot in the settings in the top right- Yes ... and then under Personalization. [01:20:00] 

**Speaker 3:** Yes. 

**Speaker 8:** Um- 

**Speaker 3:** So if you go... It's in all the tools, but in Copilot, you go to Personalization. You can give it, uh, custom instruction 

**Speaker 2:** You can say always, always use, um, cited information, you know, whatever, like to prevent- 

**Speaker 3:** Yeah.

Yeah, yeah, yeah. You can see here, give honest feedback, give you... So you give it all the instruction, and this is how you kind of modify, like, what type of, of, uh, of response. Give it the personality, basically. So you don't have to type those. Now, it also sometimes, if you do that, will save you some time and some issues, but if you are working on a different thing, I find it sometimes difficult.

So I don't personally personalize. I like to personalize it in the prompt, so I'm always in control. Because keep in mind, if you give it an instruction in the back, it's gonna always follow those instructions unless you tell it not to follow those instructions. So [01:21:00] if I put here be funny, it's gonna be all the time funny, but I don't want it to be funny all the time.

So that's one way to think about it, too. But yes, you can personalize all of those tools. You can also, um, create saved memories. So this is also important in, in Copilot and other tools. What that means is we have short memory, long memory. Short memory is gonna remember the previous prompts. Long memory is gonna take some information from prompts that you did in the past, and that can be good in a way it's gonna give you some information, uh, on a previous prompt, so it kind of tailor it for that, and it can be bad and sometimes because it can tailor the answer based on previous stuff that you put in it, and you might not want to do that.

So if you don't want it to do that, you can deactivate it here, or you can say in your prompt, "Don't use previous memory," or, "Don't use previous prompts." [01:22:00] 

**Speaker 2:** Last week you had mentioned something about taking information from one language model from ChatGPT and being able to transfer it to Claude. So can we do the same for, say, from ChatGPT to this?

Like, how do we do that? 

**Speaker 3:** Yeah. So, so I... You can write the perfect prompt in ChatGPT, paste it here. So, so I, I ask it actually to write the perfect prompt. Now, to do that, to be honest, is not gonna be probably that useful. What I found in those tools is that how they work, uh, it's might be different to complete the work.

It's more like the agentic part of it rather than just the questions and answers. If your goal, again, to do summary, questions and answer, analyzing data, you could do that in Copilot. And keep in mind, you're already using GPT 5.5. So this is why [01:23:00] I said, you know, honestly, at one point, if, if, if you, if you get used to the user interface of Copilot, you probably get around eighty-five percent of the stuff that you can do with the other tools.

When they release Copilot Work, it becomes, I think... I wouldn't say comparable to the other tools, but, but way good enough that you get what you want out of it. 

**Speaker 2:** Sorry. No, I meant like all my prompts in ChatGPT and all the data, how can it be... how can I transfer it to Copilot? 

**Speaker 3:** I don't know if you can do it from C- unless copy it and paste it.

Uh- Mm-hmm ... you can do it from ChatGPT to Claude because Claude will enable you to share that, but I don't know if you can do it to Copilot. So you can just copy and paste basically.

**Speaker:** All right. [01:24:00] Let's build a, a discharge summary disaster. You have a few minutes

**Speaker 9:** I have a question to follow up on Darren's question. So, I mean, we talked about not personalizing or th-the ability to personalize the output here, but can you also, like, make an agent to then help you with the same format? So in this case, if you're always using this function to, like, get a discharge summary, you make an agent to set the parameters for that?

Or we-- maybe we'll get to that in a future week, but- Yeah. Um. So with the agent- Just curious for, like, a very specific task, if you don't wanna, like, personalize it across the board for your use, but for a very specific modality or task. Correct. Can you leverage that? 

**Speaker 3:** Yes. So I build a Heme agent So sort of a [01:25:00] hematology consult agent.

And then the idea here in the agent as you build it, you will go back to, uh ... Show you here. So you give it an instructions. You give it a specific knowledge base So could be the internet, could be your email, could be like a set of, let's say, five articles. You give it some capabilities, meaning is, are you gonna connect it to like, uh, Excel or other things?

And in here, to your point, this is how I give it the instruction. So the instruction for my agents: When discussing diagnosis and treatment, provide guideline-based recommendations. Always cite sources. Don't give ca- speculative advice. Maintain an academic, precise, and professional tone. Uh, begin by analyzing the case I provide and then go through it systemically.

So [01:26:00] by doing that, then I don't have to put a lot of prompts Or wherever the user is using that, because this is intended, at least for our nurse practitioner to go and use and say, "Ah, I have a 50-year-old who came into me with anemia and these symptoms. What is the differential diagnosis and workup I need to think about?"

So yes, you can do all of that in the agent structure here

The ones that Darren was talking about is, is more for the entire, uh, for, for your entire experience on, on the tool

**Speaker:** All right. Did anybody write the discharge from hell? Yeah. Where is it? 

**Speaker 5:** In the chat. 

**Speaker:** Is it? Well, I don't see anything in the chat. [01:27:00] 

**Speaker 5:** It's, it's right there. There you go. Didn't write that one- Oh ... with the prompt. Yeah. Oh. This one. Okay. Then Sandra wrote one underneath. Yeah. "

**Speaker 3:** Agonize the physician and write a brief discharge summary.

**Speaker 5:** Inaccurate complete." That's Sandra. Yeah. 

**Speaker 3:** Yeah. What is missing 

**Speaker:** here?

What is missing? Doesn't say who the audience is. So context. What else?

**Speaker 6:** But it, it says for the patient, so it's not the audience 

**Speaker 2:** It's not discharge instructions, it's a discharge summary. But I thought discharge summary is a document which is pretty much the same for any hospital, so why do you need context if, if it understands what a discharge summary is? 

**Speaker 3:** Correct. But the context is, is, um, are you-- [01:28:00] Like, you could give it How do w-what discharge, d-discharging, discharging patients from trauma medicine, oncology patient?

**Speaker 5:** Right. Got it. That, that, that's why I put I'm an ED physician because it was the assumption is it's an ED. That's ... It was a quick ... It's a different kind of ... I'm not a, I'm not really that physician, so that's why. I just went with- Yeah ... the ED because it would be shorter. 

**Speaker 3:** Yeah. Straightforward with the information.

All right, let's see. Shamila, uh, as a internal medicine resident creating a hospital discharge summary for patients admitted, uh, using only the information, the chart. If the information is missing, explicitly say this, maintain professional tone, create a review of each of the problem. All right. You have some guardrails.

So we, we didn't put guardrails for the hallucination. I think, Shamila, you put some, so let's, let's, uh, let's go to Copilot and, and see how did you [01:29:00] do? Or this prompt

Now, I did not use the previous, um... This is a new, by the way. Oh, you got eight, eight point five. Great. So clear role definition, well-defined task, you get nine out of 10. Strong constraints, nine out of 10. Structured output, eight out of 10. You specify. And appropriate tone, eight out of 10. Areas to improve, it has to give you criticism.

You know, hate that. Maybe I should say don't be criti- uh, critical. Ambiguity in structure. Ambiguity. List the required elements, but don't define exact output format. Missing prioritization. It deducted- Ooh ... half a point. Sentence constraint could conflict. Five to six sentences per problem may be [01:30:00] inefficient or unnatural for simpler issues.

All right. Let's do one more, and then we all go to enjoy life. Uh, let's see

All right. This one Oh The research paper shortcut, the reviewer two trap. Summarize this paper. AI gives a TED Talk instead of critique. No critical appraisal. Okay, so you have a research paper What would you, um, how would you extract information 

**Speaker:** from that research paper?[01:31:00] 

Let's see if you guys paste anything

**Speaker 4:** Any taker? 

**Speaker:** Writing it up[01:32:00] 

Some of you 

**Speaker 3:** got scared now because- No ... Copilot is warning you. 

**Speaker 5:** No. This is lo- this is longer. This is 

**Speaker 3:** It's just like read every, every single method. Look at the method. Identify the problems. I used to do that, uh, when I asked to review papers, I was like, "Huh." Actually, if you, you upload to ChatGPT or Copilot and say, "You are a reviewer, identify 15 problems in the paper," it does a really good job.

But now journals are restricting that, so just keep, keep that in mind- Yep ... if you're doing that. 

**Speaker 5:** Yeah. Well- 

**Speaker 3:** Acting as a author, create an academic abstract for no more than 300 words summarizing the problem, review of the research, research design, limitations, strength, and weakness Um All right. Any other takers?

Write a professor and create detailed outline of this paper. Include all [01:33:00] content to add. The outline should be structure and bullets. Include references. That's nice. All right. I'm gonna take this. Let's score it

**Speaker:** Oh, boy. 

**Speaker 3:** Now see here, just gonna put this, and I don't say score or anything, and it's gonna score it. So this is sort of the short memory, where it's gonna rely on the previous prompt, and it's gonna... See, I didn't say score or

do anything. I just pasted it. Get eight. That's good. Not bad. So clear. No, no, it's good. It's not gonna give you ten. Yeah. Okay, guys? You're not gonna get 10 no matter what you do, so- ... it's gonna always critique you. So clear all, um, define task, constraints on fidelity. Let's see the limitations. Missing source context.

Well, that's not your fault, so- Oh, because I didn't attach the paper ... you did not upload. Yeah. Yeah. So, yeah, well, so we'll give you [01:34:00] one. We'll g- so you scored nine. So if- I was gonna 

**Speaker 10:** say, you got a nine. It won't be 

**Speaker 3:** a ten. Yeah, you scored nine. Lack of structural schema, the outline is not anchored to a recognized academic structure.

Eh, that's... You know, s- again, sometimes that's not what you want, right? No depth, expectations detailed on subject. Ah. Eh. Eh, look, I mean, I've done this with AI sometimes and ask it a question or something, and it comes back, and I'll be like, "Eh, this doesn't make any sense," so I just ignore it. This is why sometimes AI is challenging or, or these models are challenging because for, for, for somebody who knows things and know the answer, regardless of how m- much the answer is plausible, you can say, "Well, this is garbage."

I worry, for example, about medical students and residents and fellows and, and trainees who don't know what perfect is. The answer is kind of like very plausible, and it can trick people, so. Perfect. Great. [01:35:00] Um, I guess that's it for this session. Hope you guys enjoy it. Any last questions before we all go enjoy our Friday?

**Speaker 10:** It was a great session. Again, 

**Speaker 5:** thank you. It's really good. Yeah. 

**Speaker 3:** All right, guys. Thanks a lot. Have a wonderful weekend, and we'll see you next Friday. 

**Speaker 10:** Have a great weekend, everyone. Have a good one. Happy Father's Day. 

**Speaker 3:** Bye. Thank you.

