# W2 – Guardrails & RLHF

[00:00:00] 


## Guardrails & RLHF

**Speaker 3:** Right, this is... A quick important thing sometimes get missed. This is one of the most important thing that OpenAI did with large language models. So if you think about large language models, GPT-1, GPT-2, and the attempt from other companies before. They have a lot of attempts to put those chatbot where you ask it a questions and answer it to you.

The challenge at that time was if you go-- So if you go on a GPT-1, this is the first model that came out, and say, "Okay, well, I get I... You..." Actually, they made it open source, so you can download it on your laptop. And at that time you, you should go, you can go and say, "Well, give me five steps to build a nuclear bomb."

And the model will be like, "Oh, these are the five steps to build nuclear bomb." Why? Because it has the data in it, so there is no guardrails. So they start seeing, for example in previous attempt, if you curse at the model, the model will curse back at you. [00:01:00] Now, you don't want that to be happening in the public, so you have to put guardrails But putting guardrails on like millions of questions is not an easy task.

So what they did, and this is-- this step is very important, get missed a lot. So they did something called reinforcement learning from human feedback. So what they did, they took the questions and answers for like difficult questions, OpenAI did. They collected the response. They have a human re- human review it one by one, rank it or flag it.

This is good, this is bad. These humans were actually in, in Kenya, in Africa because they pay them like very minimal amount of money 'cause this has cost a lot of money. 'Cause it's not one, two, three response. We're talking about hundred thousands responses we need to, to, to, code. And then they build this reinforcement learning, and reinforcement [00:02:00] learning meaning y- you can't also...

I mean, just one by one build that. But what they did, they took the, responses and then have the model through reinforcement say, "Yeah, if something similar come up, you know, you should block it or put the guardrails on it." This is why if you go on ChatGPT today, which you please don't, but if you say, "Hey, help me build a nuclear bomb."

It'll say, "No, I'm not gonna help you to do that." Or if you say, "Oh, I wanna cheat in, in Sony game. Help me cheat." It's gonna flag you. Say, "No, no, I can't. I'm a large language model, I can't help you do bad things." So these are the guardrails that enable the model to be technically safe. What we will learn next week is how do we get around that.

Something called jailbreaking, which is how do you get the model to do something that it's not supposed to do by indirectly asking the question? [00:03:00] And this is why, you know, some of the report, this is why they shut down Fable because part of it is, is that, it's kind of degraded you. I, I don't wanna go there because there are two sides to of that story.

but, some people were able to break that model, and by breaking that model you can do bad things. So we have to be careful with, with these models, especially in healthcare. If you put a guardrail on a model, for example, not to accept PHI There's a way around it. That's a problem for us in healthcare, and that's what we will learn next week.

But, but keep this in mind. Reinforcement learning with the human feedback was very important for the success of ChatGPT because that's enabled the model to be safe when you ask it very difficult questions or a question that it shouldn't answer it for you



