# W2 – Large Language Models

[00:00:00] 


## Large Language Models

**Speaker 3:** Because now instead of running word by word through each layer, we go to the vector database, and we pull up all of those tokens and, and vectors basically. So it becomes easier to process the text. That- Development led to the development of large language models or LLMs. And what a large language model is, it simply is an AI program designed to process and generate text.

So it's a language model that mimic human language. Where, where large come from? This trains on trillions of tokens. It has pil- billions of parameters and pre-tuned and fine-tuned on tasks. So what OpenAI did back in the days in two thousand seventeen, eighteen, and nineteen, they went to the internet and they took all the [00:01:00] text in the internet.

So imagine now you have the internet text. They turn it into tokens, and then they start build this transformers model but, but maybe more like, in a more scalable way. So they have billions of parameters of these models. I mean, I remember when, when... So you have GPT 1, GPT 2. GPT 3.5, this is the large language models from OpenAI, that's the first time ChatGPT came in.

So ChatGPT is the user interface. It's how you look at it, basically. And in the, the first time when, ChatGPT came out, that was like 3.5. So it's the model that evolved from GPT 1 to 2 to... And, and they say 3.5 at that time is trained on like a-- I forgot the exact number, but we're talking about, billions of parameters.

Then 4 was trained on trillions, and then they stopped saying how much data is trained on it. But, but that's what happened, and this is [00:02:00] why if you go back at that time, the New York Times and other publishers start suing OpenAI because they took their content without their permission to train these models.


## Model Types

**Speaker 3:** So we have two types of models. We have general-purpose model, pre-trained on massive amount of data for general purpose. So everything you use in Copilot, Claude, and OpenAI, these are general-purpose models. So when we talked last time, when we showed the tool, and we're gonna talk again when we show Copilot.

Copilot is the user interface. It's not the large language model. The large language model, I can go up and choose. GPT 5.5, that's the most recent model from OpenAI. Opus 4.8, that's the recent model from Claude. You probably heard in the news there was a new model called [00:03:00] Fable from Claude that was stopped now.

There's a dis- dispute with the government among the model and all of the stuff. Let's park that on the side, but that's the name of the model. There are Chinese models that are out there: DeepSeek, Kiwi, Owen. So these are general-purpose model. Now, what you can do, there are two types of model. There are open source models, and there are foundation or frontier models.

Frontier models like GPT 5.5, Claude, and other models, those ones you cannot download. They're not open to the public. You have to pay for it. Where there are open source model, the open source model is where you take the model, you can download it, not all of them, but the, the smaller one, on your laptop and use it for free.[00:04:00] 


## Fine-tuning vs. Pointing (RAG)

**Speaker 3:** So those typically are the Chinese models DeepSeek, Kiwi. So that's what we call it open source models. Fine-tune models. You can take an open source model, train it on your data, and that becomes a fine-tuned model. So meaning that you can focus the expertise of that model on your own data. In my experience, I can tell you fine-tuning the models used to be something interesting.

Any general purpose models will outperform fine-tune models. It just waste of time now because the race and, and the amount of complexity of these models, the amount of, of, e-evolution of these models, it's, it's insane. And fine-tuning the models takes time, effort, and energy, and compute, and costs money.[00:05:00] 

We'll talk about reinforcement learning from a human feedback in a second. Sandra? 

**Speaker 2:** Is, is UpToDate a fine-tuned model? 

**Speaker 3:** Yes. Just to get context. So I, I think so. I think so. I, I shouldn't say yes. So the idea there is that it's trained on UpToDate models. Now, what you also can do instead of training it on it...

So this is why I'm not one hundred percent sure. You can take general purpose model and point it to the context on UpToDate instead of training it on that context, and that pointing- In my experience and re-research that I have done, it's actually typically yield better result compared to fine-tuned models.

So that's what open evidence has basically, 

**Speaker 2:** Can, can I ask a follow-up? 

**Speaker 3:** Yeah, yeah. Sorry. Please. 

**Speaker 2:** Sorry. So, so when you [00:06:00] say point it, you're talk... I think you're talking about prompts, which you said you're gonna cover later. But is it basically going into one of the general-purpose models and say, "Use up-to-date and other sources to explain this or figure out this question for me?"

Is that, is that what you mean? 

**Speaker 3:** Right. So, so think about it this way. So let's say you have ten review articles about a disease. You take those review articles and put them in a folder. And what you can do, you can take large language model and say... So, so let's, let's process this. How's that, how's that gonna work, right?

You're gonna take those PDFs which has text, right? You're gonna turn, turn that text into tokens. You're gonna put it, do embedding, and you're gonna put it on a vector database. Yeah? So all of this becomes a vector database. Then you're gonna [00:07:00] point the large language models to that vector database and say, "If I ask you any questions, you just answered from that vector database."

Right? So this is how it works. And then what you can do, you can engineer it to say, "If the answer is not in that vector database, don't make it up." Or, "If the answer is not there, go search the internet and make it up." And this is how you kind of build that workflow.

Where fine-tuning, you're gonna take that ten documents and you're gonna come up with the questions and answer, and then you're gonna go and then tell the model, "If I ask you this question, this is the answer. If I ask you the question, this is the answer." And then retrain, change the parameters of the models, and that becomes fine-tuned model.

This is why it takes time, energy, because you have to label the data and you have to train it, and it takes a lot of time and effort and money. And honestly, in my experience, the one that you point the large language model to, [00:08:00] it, it outperformed the fine-tuning. Does that make sense?

No 

**Speaker 4:** No, totally it does. Thank you. 

**Speaker 3:** Perfect. It's the same thing, by the way, if you think about it from EMR, from, from, like, Epic. you have all this data in Epic, and I now can point, let's say, GPT-4 or 5.5 to that Epic data and extract the information from it. So, so that's when, it works. This is just to show you the evolution of large language models.


## Evolution of GPT Models

**Speaker 3:** As we discussed, transformers came out in two thousand and seventeen. They're like, BERT and GPT-2 in the '18 and '19 were, like, hot until GPT-3 came, and you can see billions of parameters at that time. And then the release of ChatGPT, which was GPT-3.5, and now we have all of these models that evolve and continue to evolve.

And there [00:09:00] are, like, websites where they can rank them. And I can tell you what's interesting about this, that some of these models, they rank high in physics, in, in math and software engineering, has nothing to do with, with healthcare questions. And I still think we need to develop better evaluation of these models in healthcare, and that's something of the research that I'm very interested in and we're working on, too.

