# W2 – Why Models Hallucinate

[00:00:00] 


## Why Models Hallucinate

**Speaker 3:** All right. So how these large language models work. So we talked about the transformers. We talked about the positioning, encoding, the vector database. What the model actually does here is trying to give probability. So, so once you ask a question, the large language model's gonna go to that vector database we described.

It's gonna start pulling token by token, right? Now, as it's pulling those tokens, it's gonna put the token and gonna predict the probability of the next word based on the word before or the token before. So, for example, if you put a prompt, "The patient was prescribed five hundred milligrams of," it's gonna come back and say, "Okay, it could be amoxicillin, acetaminophen, metformin."

So it's gonna have a probability of words and then gonna predict that the highest probability is gonna be amoxicillin. So think about that. This is how these models work. [00:01:00] So as it's putting the text out, it's kind of predicting the next text. So this is open the whole question, are these models intelligent or just predicting the next text?

So that's number one, though. It sounds intelligent because it's putting words together, and it used to be back in the days that it, anytime, on the GPT-3.5 and 4, it's like, it's like putting a lot of words. It's, like, too wordy. Now they come around and, and actually improve that. But this is also why these models hallucinate.

Why? Well, if it have the next word and the probability of that word is wrong, predicting it wrong, it looks to you hallucination. So for example, if it comes and say the patient was prescribed five hundred milligram of, instead of saying amoxicillin, said metformin. Metformin has five hundred milligram too.

To you, oh, the model hallucinate because it's pre-- I wasn't talking about [00:02:00] metformin, I was talking about amoxicillin. To the model, it did not. It could be metformin, it could be amoxicillin. This is why hallucination is interesting. So hallucination dropped dramatically on recent models, but cannot be zero because there was actually a big paper, big nice paper coming out of OpenAI.

There are some stuff also we as humans don't a-agree on. So how we... And, and when we see it in the model, we say this is a hallucination, this is incorrect. Well, but if we don't agree on something, how is that is incorrect? So now does the model make mistakes? Yes. In fact, in healthcare, we have research showing on a complex oncological questions, these models have a-- even the best ones have about thirty, forty percent hallucination rate, making up stuff that's not in the guidelines, not sticking up with the guidelines.

Now you know why, [00:03:00] because it's predicting the next word, and the next word is wrong or putting like treatment together, and then that treatment doesn't exist. This is why traditionally these models were not good in references. Think about it. So I'm gonna pull up token by token. So I can come up with a reference for Aziz Nazha that doesn't exist because if I predict the next author wrong, the whole reference is wrong.

And they used to be terrible at this. Now they improve that by, they sort of engineering a long context of some of those references. So, so now I'm hoping that you sort of understand to, to a deeper level why these models-- how they work, but why also hallucinate. So to wrap this up Models don't understand text, they understand numbers.

