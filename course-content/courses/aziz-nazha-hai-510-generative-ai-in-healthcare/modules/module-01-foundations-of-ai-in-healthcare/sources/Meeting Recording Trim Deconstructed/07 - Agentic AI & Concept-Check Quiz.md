# 07 - Agentic AI & Concept-Check Quiz

[00:00:00] 


## From Chatbots to Agents

**Speaker:** Uh, I will quickly talk about agentic AI just to stay on time. So, so now we evolved if, if you-- if, if as you see from machine learning, deep learning, where we are talking about discriminative prediction, you know, bleed, no bleed, chest X-ray, pneumonia, no pneumonia, to generative system. That's what we used to call a chatbot, right?

So we'll go on ChatGPT, ask a question, it spit out the question to me Or build an image or build in video. And now we start moving, I would say even in '23, I, I, I build agents in, in '23. '25 becomes the top of the hype cycle, agents and multi-agent system. A-and now it's, it's, it's still there's hype behind it, and there's misunderstanding what an agent is.

So, so I hope to, to clarify here and, and in the hope of this course, by the end of the course you build one or you build a team of agents. So [00:01:00] this is also tricky because the definition is not universal, and I feel like sometimes people mix things between agents and autonomy. So, you will hear people say, "Oh, if the agent is not operating on its own, it's not an agent."

Well, that's not true. You could have an agent that can give you... For example, go on Expedia website, find information and before it make the reservation for the flight, it discuss it with you without just automatically making that reservation. So autonomy has nothing to do, in my opinion, with agents So, so we need to separate that.


## What Makes Something an Agent

**Speaker:** But, but an idea behind an agent, think about it like a system that can perceive, like can understand data. So when you go to that system, you, you give it instruction, it's gonna understand it. So it's have this perceive. It can reason. So when you give it the instruction, especially for [00:02:00] complex task, it's gonna take those complex tasks and kind of like chop them down and also understand, like, what is this task needs to, to, to do and, and sort of come up with a plan to do this complex task.

What separate an agent, in my opinion, from chatbot, is an action. The agent has to take an action, has to develop, has to use a tool to, again, make a reservation, build a slides deck for you. That's an action, right? And now what we start having is systems that can also learn. So the agent can build the slides, go back and say, "Yeah, I need to modify this, and I need to modify this."

And then you give it sort of some instruction, then it learns the way you develop the slides, and then in future slides use your way or use its own way. [00:03:00] So the systems is getting better. There was a recent paper just came out of, of Anthropic talking about this, what we-- they call it recursive learning, and how much these systems now become scary in a way that they learned on their own and then they start improving and improving.

And again, there's some hype to it, of course, but, but also there's some reality. And, and this is where, some of the stuff that we need to, to watch. It's very exciting, but also the capability is moving very quickly. I see a question. 

**Speaker 6:** Hi. Yes, just to, make sure I understand. So, like, ChatGPT, as it stands right now, is an AI agent in that I can give it a document, ask it to make slides to me, and then tell it to improve the slides with some instruction?

**Speaker:** Yes. It's, it's all of those tools move to become agentic. All of them. Claude. The, the, the, the worst agent or tool is Copilot, but, but all of [00:04:00] them, they became agentic. So if you go-- And I will show you when we talk about the tools, how it's think, plan, execute. That's, to me, agentic. It's not a chatbot anymore.

So to, to that extent, yes, you're correct. All of them become agents, basically. So this is just to kind of tie it up to your question. 


## Tools, Memory & Guardrails

**Speaker:** So what does make it an agent? It's now, depending on the tools, you have the capabilities of connecting ChatGPT, for example, to multiple tools. And that give it a lot of power.

So I can connect it to my Google Drive and my SharePoint so it can extract the information. In fact, today I can connect it-- connect, for example, Claude to my desktop, and I connect it to a folder, and I can, in the prompt, say, "Go to that folder, find this lecture, [00:05:00] add slide number five on this lecture," and it will go find the lecture, add the slide, and then push that lecture back in the folder without me going and uploading and doing all of this stuff.

You can connect it, obviously, to the EHR. You can connect it to, to pay your bills, uh, to your credit card, and that's the beauty of this. I can connect it to a hundred tools. It also has memory. So if you go on ChatGPT, it has short memory. So short memory meaning it's gonna remember the previous prompt. So you have this chain of prompts, it's gonna remember that.

But also now it has long memory, and that memory is getting bigger and bigger, which is, which is important. Long memory meaning it's gonna remember previous prompts. So if you go on ChatGPT today, sometimes you feel like, "Oh, it's kind of sneaked in some of the information from previous, prompts." What, what they're trying to do is trying to personalize the, the outcome and the output, so sort of [00:06:00] remember some of your style, your situation, and kind of answer that.

and sometimes becomes annoying because you don't want it to use that. So you could either tell it not use it or go and shut down what they call it the long memory. What I will show you now most of those system, if not all of them, they have a planning and thinking and skills. And the skills is, is like sort of a set of instructions that the system use to complete a task.

It can retrieve information, so if you upload a PDF document, it's gonna dissect that document and extract that information. You could point it to a SharePoint or a set of documents and extract that information. Some of those systems in a multi-agent system, it can delegate, meaning you have an orchestrator agent, you have a small sub-agents.

The sub-agents can perform a task with this tool. [00:07:00] The sub-agent can perform a task with this tool. The orchestrator agent come up with a plan, assign it to the sub-agent. Those sub-agents go execute that small task and bring it back to the master agent or the orchestrator. I'll show you that how it works in some of the tools.

And also we have some, some guardrails. If you go today on ChatGPT and say, "Help me build a nuclear bomb," it's gonna tell you, "No, I'm not gonna help you." Or, or if, if you wanna, for example, do like a, a sha- uh, shady things. It's not... So, so there are some guardrails. However, there are ways to get around those guardrails, and that's what we're gonna learn in module, three 


## Multi-Agent Systems & Workflows

**Speaker:** This is what I was talking about, the multi-agent system.

This has evolved, by the way. It's just the last two months, it's, it's getting crazy how this stuff is changing. If I'm giving you this lecture in December twenty twenty-five, ninety percent of what I said now would have been different. So it's [00:08:00] crazy. But, but you see now this multi-agent systems where you have an orchestrator agent, as I mentioned, and some sub-agents that can perform a task.

The orchestrator agent come up with a plan and then assign it to sub-agents. Anthropic has a different thing. So instead of using agents, they use what they call it skills. So set of instruction. Nobody knows, at least to my knowledge today, because this is new, a multi-agent system is better than skills. In my experience, depend on the case.

Some cases, multi-agent system is better than skills. In some cases, skills is enough. You don't need multi-agent system. We'll dive deep into this stuff in module four because this is really becoming like deeper and deeper now we're going into the technology. And again, this, this sort of evolving every day, new techno-- new terminology coming.

So you have [00:09:00] agentic workflow versus agent versus multi-agents versus skills and, and I can have like ten other slides of some of those, terminologies. But to simplify, you could have what we call it a workflow. So you have agents, you don't need one. You can have a team of agents, and then you build a workflow where some of the tasks are done by agents, or some of them can be done by human, and some of them can be done by both, or the entire workflow can be done by agent.

But then it's sort of more like structured. So the first agent will do this, the second agent will do that, the third agent will do this, and then you run the workflow. That becomes an agentic workflow. A single agent, again, you can build an agent, you can have data On a specific topic [00:10:00] and point that agent to that data.

So let's say you want to build an agent that can help you, answer questions about HR in, in, in, in Jefferson. So if you have a question about your benefits, what you will do, you take all of these HR documents, let's say benefit documents, and you point the agent to them to retrieve that information. So if you go and ask, you know, "What is my four oh one K matching?"

And those things are gonna go to that document, extract this information, give it to you. That's a single-agent simple. We call it RAG agent, retri-retrieval augmented, generation agent. That's very simple agent. Multi-agent system, as we discussed, you have multiple experts working together, uh, and trying to complete, uh, a broad and complex task So, all right.

Let's, 


## Concept-Check Quiz

**Speaker:** let's see if, if this resonate. So, uh, an [00:11:00] AI that flagged diabetic retinopathy in retinal photograph, is that generative or discriminative AI? Sharol. 

**Speaker 6:** Discriminative. 

**Speaker:** Great. An AI draft a discharge summary from patient's chart 

**Speaker 3:** Generative. Generative Right. AI 

**Speaker:** predict thirty-day admission risk as high versus low.

**Speaker 3:** Discriminative 

**Speaker:** Eight. An A- AI designs a brand-new molecule to bind to a cancer target. 

**Speaker 2:** Generative. 

**Speaker 6:** Generative. 

**Speaker:** An AI answer patient questions about their medication in plain language. 

**Speaker 6:** Generative 

**Speaker:** Yes, that's generative AI. Perfect. All right. Now, well, I wanna keep with my promise, and, and this took, longer than I thought.

