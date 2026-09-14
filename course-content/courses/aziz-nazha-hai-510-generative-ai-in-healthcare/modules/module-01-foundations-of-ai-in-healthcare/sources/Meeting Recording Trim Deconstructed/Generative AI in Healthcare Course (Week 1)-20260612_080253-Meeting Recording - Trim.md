# Generative AI in Healthcare Course (Week 1)-20260612\_080253-Meeting Recording - Trim

**Speaker:** [00:00:00] Right? Perfect. And then let's

Share the slides. Perfect. So w-welcome everyone and, and, and thank you very much for joining the course. Uh, I'm very happy and delighted to have all of you part of, uh, this course. This is a unique course, I think, in, in it's offered through the population... uh, the College of Population Health at, uh, Thomas Jefferson University.

My name is Aziz Nazha. I'm the Executive Director of AI, uh, Workforce Transformation and Education at Jefferson. What we're trying to do at Jefferson is, is trying to do a small task, which is: how do we educate sixty-five thousand people on AI? Um, and this is one of the efforts that we have been doing. We have been doing workshops.

This course will be officially offered for students in, in September, and I think it's a unique course in the university. Uh, I don't see that many of these courses across any other university, so I think that will give us unique [00:01:00] opportunity, uh, uh, to provide this course to our students. We will be also providing this education as much as we can to, uh, faculty and departments and across not just Jefferson Health, the university, Jefferson Health, and also the health plan So wanna quickly introduce you to the course.

I sent the syllabus, I sent the A preferred reading if you have some times, there are some articles there that I think it's worth, uh, reviewing. We will review some of those articles in the course, but, but if you, if you wanna take a look at some of these, uh, articles. Um, as everybody knows, AI is moving so quickly, it's everywhere.

It's gonna take all our jobs, and we're gonna be jobless, um, uh, one day which is not true by the way but, but it's, it's a wonderful technology. And I think if we put the hype on the side, we take a full advantage of this technology, we will be [00:02:00] able, hopefully, to have a significant impact on healthcare and hopefully...

Uh, that's what, what actually keep me interested in this technology, keep me working with this technology is I'm looking forward to the day that we have the healthcare that we all want. The healthcare where you can call a physician and get an appointment tomorrow. You have less errors. You, you have better, faster delivery of, of healthcare for all of us, uh, across, uh, the world, actually.

So, so this is what I do believe that the technology will bring to us if we know how to use it in healthcare. What we're hoping in this course is really try to, uh, give you the basics, but also the application of the technology in healthcare. Um, I think one of the biggest challenges today for the technology in healthcare is not the technology itself, the technology is amazing, is how do we upskill our workforce, physicians, uh, and, and, and, uh, shared services, [00:03:00] everybody, not just physicians and clinicians and everybody on, on the, uh, skills that we need to do with AI.

So how do we upscale our workforce? How do we reskill our workforce in the age of AI? And that's very difficult to do. I don't think any healthcare system or university figured that out, and that's what we're trying to do here at Jefferson, where we-- through this education, we're trying to bring those skills up, uh, of our workforce.

So the format as, as we tried here, again, this is, this is the first trial, so any feedback from you guys w-will be very useful. Uh, this is synchronous virtual. It's live. I do believe in live seminars, and I do believe actually in personal one. To be honest with you, the personal one, it's, it's, uh, there's something about, uh, about it, and I've done those workshop in person, I can tell you it's a different experience.

In person obviously, it's gonna be really hard to bring also people in person, [00:04:00] so, so we're doing this virtual synchronous. It's four weeks. Uh, uh, Fourth of July will be... We're gonna skip that Friday, so it's gonna be the Friday after that. This is the first Friday. The format we're trying to do here... So this is the condensed course that we will be offering in the fall.

In the fall, it's gonna be seven weeks asynchronous Course. So we try to condense it in four weeks, uh, so this is why we, we, we say two hours per week. The idea will have forty-five minutes lecture, that's the didactic lectures, give you some, uh, time, uh, to relax, and then we come back, we have hands-on lab. To me, that's the most important part of this.

Lectures, y- I can record it, send it to you, you can watch it. But the hands-on lab where, where you get your, your hands dirty. We try to put it on Friday, uh, uh, from eight to ten. What is the best time to do it? I don't know. I mean, some people are busy on Friday, but, but we came up with this, [00:05:00] uh, time, so hopefully g- that's will work for you.

Um, and then no, uh, prerequisite or programming needed. In fa- in fact, we're gonna use the tools to help us to build, uh, everything here. This course designed for, for workforce in Jefferson, so you, you can be a, a physician, you can be a faculty, you can be, uh, an admin taking that course. Anybody who works and touch in healthcare would qualify to take this course, basically.

So what you will learn is we start this week, and we'll talk more in the next slide, the basics of AI and, and, and, uh, believe it or not, it's, it's, um... The more I go and give those talks and ask people, "What is AI? What is machine learning? What is agentic AI?" You will be surprised how much, uh, uh, like, that knowledge needs to be injected i-in the workforce, so we all understand those basics.

But also now we start having new de-- terminologies [00:06:00] like LLMs and agentic AI and what does that mean and how do we talk to these models with the prompt engineering. Um, and then the goal, obviously, in, in the course in the fall, when we work with the students throughout the course, at the end, they will have a project.

They need to deliver an agent or multi-agent system to solve healthcare problem. It's become much easier to do that. The expectation o-obviously in this course to do that, uh, and we will try to do it. Now, the last, uh, co-- uh, uh, uh, module is gonna be didactic, but the, the lab in that module where we're gonna start building or maybe just showing you some of the people who build agents.

So the expectation is that hopefully by the end of this course, you come up with a project and you build an agent or agentic workflow that solve a problem for you. Uh, and I think if you are able to do that, that's a big success of this, uh, course. [00:07:00] So this is week one. So today what we will be talking about is the foundation of AI.

So what is AI? What is generative AI? How it's applied in healthcare. In the lab section, we will visit, uh, the tools. I'll try to give you as many tools. They are growing every day. Their functionality is growing every day. So I'm gonna mention some of them for you. You will go back. My hope is to start experimenting with those tools a-and then pick up the tool that makes sense to you.

So, so, so we'll start, uh, this is for this week. Next week we'll dive deep into what large language models are, um, how they work. I think, uh, sort of some of the mechanics, but we're not gonna talk about the math. So, so don't worry about that, is like how these models, uh, work. But, but just dive deeper 'cause I think if we understand that deeply, we will be able to understand why these models sometimes hallucinate, why they make up stuff, why they don't understand what we're saying to [00:08:00] them.

And then we're gonna focus mainly on prompt engineering. How do we talk to these models? Uh, which is slightly different than how we talk to human, although prompt engineering now we need to do less prompting, I have to say, but, but still, uh, if you, uh, craft a good prompt, you're gonna get, uh, uh, a good result out.

And then in the lab section, we're gonna practice that. So you will be practicing prompts and how do you, uh, uh, get, uh, a good prompt. Week three is my favorite because at that time we will start talking about the challenges of this technology and when it's applied to healthcare. And this is extreme, extremely important.

Um, and uh, I feel like a lot of education is always focused on the upside and the wonderful thing we can do with the technology, which is great, but also we need to focus on the shortcoming and the difficulty of applying this technology in healthcare. Because when we address those, then we can take this technology further.

[00:09:00] And especially in our industry where we have data privacy, HIPAA, patients, uh, information. So, so it's not a typical application of, of technology. Uh, so, so this is where we, we start talking about this hallucination, bias, fairness. And then when we go to the lab, this is why it's my favorite, then you through the lab have to go and bias ChatGPT, for example, or break...

jailbreak ChatGPT, and so forth. And then finally, the last week we will be talking about agentic AI, how it's applied in healthcare. We're gonna dive deeper into agents, agentic workflow, multi-agent systems, automations, um, and then hopefully, as I mentioned, is, is in the lab where we're gonna build or already build, uh, um, agents or multi-agent system that we can apply them in healthcare As we discussed, for forty-five minutes didactic, we'll give you [00:10:00] a break.

About ten minutes, we'll come back, we'll have the hands-on, uh, and probably, hopefully, we'll get you less than two hours. Uh, we will-- To me, the most important thing of this is the hands-on lab. To be honest with you, that's where, again, the learning happen, uh, more than just giving a didactic lectures and slides.

Uh, the final project, uh, here are some examples. You, you wanna build multi-agent system, a clinical decision tools. Anything you're working on, I would say doesn't have to be like, uh, uh patient-facing. Or if, if you're, if you're working i- as an admin in, in, in a department, build an agent that is useful for you, that can help you in your job.

So, so the goal is to build something that is helpful to you. That's, to me, will be the success of, of this, uh, uh, course. So, uh, hopefully you will be able to attend live. If not, we're gonna record this, we're gonna send it to you. Uh, uh, I would love to see participation, especially on the hands-on. [00:11:00] Yes, it's, it's-- this might be difficult in the virtual setting, but we're gonna try to do it, uh, uh, uh, less difficult and, and hopefully make it more interactive.

Uh, that's the hope. Um, and then we wanna experiment together, we wanna learn together. So shout out, ask questions, uh, uh, try to apply everything hands-on, uh, as much as you can. And you got my email, so if you have any questions or concern, please feel free to email me. All right. So let's... So start with, 

**Speaker 2:** uh, um- All right.

So Do you guys see this slide?

**Speaker 3:** It says found, um, introductions to AI foundations module one 

**Speaker:** Yes. Perfect. 

**Speaker 3:** Yes. 

**Speaker:** All right. Okay. So this is the didactic section. Then we have some questions, and then we will move to introduction to [00:12:00] tools. Um, I think when I put the slides-- So, um, obviously it's early in the day, but how many of you already have used AI today?

I should have framed the questions the opposite. How many of you did not use AI today?

So, so raise your hand if you did not use AI today or yesterday, because maybe today is just too early for you. But, but the whole purpose of this... It looks like Jennifer did not use AI yesterday. Is that true, Jennifer?

I think you used it. So the whole purpose of this slide 

**Speaker 4:** I didn't use it today. Sorry. I was trying to unmute. 

**Speaker:** Yeah, it's too early today. Yes. So, so yesterday. So the purpose of this slide is, is whether we realize it or not, uh, I think that's the goal of this slide, that we're using it every day. So if you're using your email, your phone, your iPhone, your, your streaming, it, it's everywhere, whether we recognize it or not.

And, and I think that's-- it's an [00:13:00] important concept, sometimes it's missed. We all consuming AI every single day. The question that, that, uh, I think is more important is how much AI we're using in our work. So ninety percent of people use ChatGPT daily, and about fifteen, twenty, probably now it's more in some of the studies, thirty percent use it in their work.

What we wanna focus on, how do we use this technology in our work? And that's what I'm hoping to get you out of this course. So what we're gonna talk in this lecture, what is AI? What is machine learning and deep learning? As we discussed, this is very important, and we're gonna dive deep into some of that description.

Even though this is not a introduction to AI course, this is generative AI. But I cannot teach generative AI if we don't understand the basics of AI, and that how this technology evolved to become generative AI. And then [00:14:00] what's the difference between generative AI and what we call a discriminative or predictive AI?

I think this is very important. Uh, so this is why we start with the AI machine learning, deep learning. We go to generative AI, and then what I'm hoping that all of you walk away from here able to distinguish between disc-discriminative and generative models. And, and then we're gonna talk about agentic AI and some of the core capabilities, and we'll give you some examples in healthcare.

Obviously, I cannot give a lot of examples just for, for the time, uh, being. So the landscape of AI has evolved, and, and you can see this sort of terminology that started in nineteen fifty is and now evolving. So it started with artificial intelligence. And then the idea at that time, and it started in the nineteen fifties, that machine can perform and do things like a human without [00:15:00] explicitly programming the machine.

So if a human can drive a car, can I make the machine drive the car without it giving me sort of like give the machine step or every single step across the way or along the way? They couldn't do it in the fifties and sixties, obviously, because they didn't have what we have today, which is data and compute.

They, they didn't have all that capability. So in the fifties, sixties, seventies, the computers were the size of this room. So they didn't have that, uh, evolution at that time. You see some spikes in the nineties when deep, uh, uh, alpha... When Deep Blue beat Kasparov in chess. And so you see, uh, some improvements over time.

But, but, uh, recently that development has accelerated, driven by data and driven by compute. Now, in the eighties and nineties, the, the terminologies were machine learning, and then that machine learning evolved to deep [00:16:00] learning, and I'll explain more, uh, about those. But the idea of machine learning and deep learning is really trying to teach algorithms with data so the algorithm can find patterns in the data and then come up with the answers or predict an answer.

So, you know, this is a dog, this is a cat. This is how when you go on Google, you will see, for example, if you type like a, a, a picture of something or name it, pull up that dog picture for you. So that's, uh, uh, part of deep learning. And then recently, and I would say just to start in the t- uh, twenty twenty, probably a little bit earlier, but, uh, when ChatGPT was released in twenty twenty-two, that sort of brought up generative AI, although it started before that.

But that's where generative AI started becoming big in the media and then generative AI, uh, evolved to agentic [00:17:00] AI, um, and, and then multi-agent systems and, and those things. So, so what is machine learning and how does it work? Um, so machine learning is when you have-- sort of one of the easiest way to think about it is, is that you have an input.

That input could be an image, could be a structured data, could be a video. You have an output, is something you're trying to predict. So in between, you have an algorithm. This algorithm could be machine learning algorithm or a deep learning algorithm. A deep learning algorithm is the idea here that you have the input layers and the output sort of mimicking the neurons in the brain.

So if you look at the neurons in our brain, we have a neuron body, and those neurons are connected to each other. So when they fire up, we, we, we talk, [00:18:00] we, we do all the tasks. If we try to mathematically represent this, this become a neural network. And deep, meaning it has multiple layers, could be a thousand layers, and that's representation of the input layer and then the output layer.

And then the prediction could be a classification problem. So we're talking about, you know, malignant lesion, non-malignant lesion, dog, cat, multi-class: dog, cat, giraffe. Or regression problem. Regression problem is a continuous number, so we're trying to build, uh, uh, uh, like a, a length of stay model. How much the patient will stay in the hospital, that's gonna be a continuous number.

Uh, house prices in Philadelphia, that's a continuous number. So there are different types of machine learning And, and th-they, uh, differ in their applications and applications in healthcare. And, and, and this is what, what, what I wanna focus on because if you take [00:19:00] machine learning and deep learning before...

If we're giving this lecture in two thousand eighteen or nineteen when I-- which, uh, what I was doing at that time, I was talking about machine learning, supervised learning, unsupervised learning, and those stuff. I wasn't talking about generative AI. So, so this is where I wanna distinguish, and I hate to say it's the old, it's not the old AI, but you know, it's evolved to generative AI.

But when we focus on machine learning and deep learning, you have supervised learning, where you, uh, sort of have a label for the data, and then you train the algorithm on that label. Unsupervised learning, you don't have labels, you don't have the data as a scatter, and then you s-asking the algorithm to structure it.

Semi-supervised learning, which is half of the data or maybe subset of the data is labeled and some of it is not, and then the algorithm try to label that data. And then reinforcement learning is trial and error, and I'll explain in the next few slides. So supervised learning, as we [00:20:00] discussed, is, is

**Speaker 3:** Just, just curious on labeled data, meaning it has, you know, some additional information with it? 

**Speaker:** Yeah, that's what I'm explaining in this slide. 

**Speaker 3:** Okay. Sorry. 

**Speaker:** Yeah. No, no problem. Yeah, please keep it interactive. So labeled data mean that you have description of the label. So I have a dataset, dogs and cats. So what I will tell the algorithm, so you would have sort of a table.

This image is a dog, and the label is a dog. This image is a dog, and the label is a dog. That's what labeled data. This is a cat, that's the label. So I take the image and I label it dog, cat, giraffe, and, and, and so forth. In healthcare, I will introduce to the, to the algorithm this is, uh, um, for example, an image.

This is a bleed, no bleed. So I will give the algorithm a CT scan, and I will label it. So on [00:21:00] this CT scan, this is a bleed. On this CT scan, no bleed. Chest X-ray, for example, right? Pneumonia, atelectasis. So that will be the labels of the data. Could be b-binary, so again, bleed, no bleed, or multi-labeled. So on chest X-ray will be atelectasis, pneumonia, uh, normal, uh, uh, pneumothorax, uh, uh congestive heart failure, cardiomegaly, and then I will label all of those.

So that's what means labeled data. And then what I ask the algorithm is to find pattern in the data, and then it spit up and say, "Okay, this is a bleed. This is no bleed." That's what the model will tell me. So if I train the data on dog or a cat and I give it a giraffe, it's gonna guess it as a dog or a cat, unless I have a label which ca-called others, and then it's gonna put it in others.

So this is part of also labeling. [00:22:00] Uh, uh, so it's gonna be dependent on the label. And the way it works, it give you probability, and then you th-- set a threshold to say, you know, above maybe fifty or above sixty, this will be a dog or will be a cat. So the idea here, again, you have the label and then the prediction, and then in between you have a machine learning algorithm or a deep learning algorithm.

Unsupervised learning, you don't have labels. You just have data. So for example, in healthcare, RNA-Seq genomic data where you're not tied to a patient and you, you sort of trying to Find the impact of that data on an outcome. So let's say response to chemotherapy, but you don't know which gene have that impact because you don't have the label.

So, so what you're asking the algorithm, go find patterns between those genes and based on those patterns, tell me [00:23:00] whether the patient gonna respond or not. So this is where it start, what we'll call it clustering. So we say, you know what? It looks like all of these genes or, or could be images or could be anything clustered together and, and then this patient in this cluster will have this outcome, and these patients in this cluster will have different outcome.

So in this example obviously there is no label, uh, in, in, in, in that. The common one obviously in, in healthcare is the clustering which we do a lot in, in genomic and, uh, multi-omic data. Now, there is something called semi-supervised 'cause you would imagine one of the challenges used to be is labeling the data, right?

Especially in healthcare, because deep learning require a lot of data, and, um, this is why back in the days it was like, "Oh yeah, artificial intelligence is not, not intelligent," because, you know, I have to label all that data. So, [00:24:00] so if I wanna build a model to, to say bleed, no bleed on the brain, I wanna take thousands of images and label them.

It's not gonna be fifty image. I mean, I know we did a lot of research with fifty image. That's not a good model. But imagine sitting and labeling, for example, ten thousand chest X-ray to say, "Oh, this is pneumonia. This is atelectasis." It, it's a lot of labor intensive, uh, work. So one technique was semi-supervised, where you have some of the data is labeled and some of it doesn't have that label, and then you're asking the algorithm, sort of train it on the labeled data and then use the algorithm to predict the label of the, uh, of the unlabeled data and then, uh, try to build a model and expedite that.

Because again, if I wanna come and say, well, I need about [00:25:00] two hundred thousand scans to build a reliable model, that's gonna be a lot of time, effort to label that data Reinforcement learning, this is-- used to be, although now we're using it more in a different way, mainly for robotics. And then the idea here, even they used to call them agent, uh, which is different than the agent we're gonna talk about in the next few slide.

But you sort of through, through action, reward, you're trying to, uh, teach the algorithm what to do. Uh, and so, um, you put the algorithm in an environment, and you give it an action. For example, go-- for a robot, go grab this, and if it does it in a certain way, you give it a reward. If it does it in a, in a, in a wrong way, you, you give it a punishment.

And then the algorithm on its own start based on reward and action, [00:26:00] improve itself. So for example, uh, one of this, we're gonna talk about reinforcement learning with the human feedback. When they kind of train, uh, the large language models, they took the output of those large la-language models, have a human review it, and then they taught the system back to say, "You know what?

This is harmful. If somebody asks this question, you shouldn't answer it." So this is how they use reinforcement learning. We use it more, uh, now it used in gaming to imp-- uh, to optimize the algorithm, uh, when they play in game to actually maximize the reward. So that's a different type of things. And again, it, it's mainly in, in also in other way in robotics All right.

So- 

**Speaker 5:** Aziz. Sorry, we have a hand up from, um- 

**Speaker 6:** Niyasha. 

**Speaker 5:** I think... Yes. Thank you. 

**Speaker 6:** Sure. Um, I was going to go back to the super... [00:27:00] the semi-supervised learning, um, and I was hoping you could just explain a little bit more about, like, quality control assurance if, um, the model is only learning off of a small subset, um, and is then predicting, um, using the large unlabeled set.

What, what are the inputs, I guess, like, that are involved to make sure that, like, it's actually learning correctly? 

**Speaker:** Yeah. So, so based on once the model, uh, produce the output, you study the output, and you have a different matrix in studying the output, right? So it's gonna be accuracy, precision, recall, uh, area under the curve, all of those, uh, false positive, uh, negative predictive value, all of those things.

So in other words, again, if you think about it like, uh, an image and, uh, let's say a CT scan, bleed, no bleed. [00:28:00] So s- uh, so you're gonna focus on the unlabeled one. So the way you do it, you split the data into training and test. You take the test data, and then you apply the final model on it. And then in that time, you're just saying bleed, no bleed, and then you're gonna go and, and score the, the system on, on that.

Obviously, for the validation, you need the labeled data 'cause you wanna make sure that the model is valid. 

**Speaker 6:** I guess I'm just curious as to, like, how this represents less work than the supervised learning. It seems like the work has just been shifted to, like, validation instead of labeling. 

**Speaker:** No, because then you're using the labeled and the algorithm to sort of label the rest of the data, if that makes sense.

So instead of having all the data labeled, you're using the label in some of that subset to label the large data through [00:29:00] that process, if it makes sense too. So you don't need all of, all of this data to be labeled. Now, that doesn't mean you might get a better model. You might not get a better model compared to fully labeled data.

But it's a way to get maybe, if you're unable to label the entire data set, to get you somewhere. But I can tell you from my experience, this is not where... it's not gonna be comparable to a full data set that has the full labels. But it's another way to get you closer there, if that makes sense. 

**Speaker 2:** Yeah. Thank you.

**Speaker:** Uh, okay. So another hand

**Speaker 7:** Uh, yeah. So I, I think I just had a follow-up to what we were discussing because it came to my mind as well. Um, how much human effort is then actually re-needed to assess reliability? You are labeling an unlabeled data set. There is a lot of, of... I, I... If you put a statistician in our room, they were like, "I'm not gonna trust AI to [00:30:00] label the data set."

Yeah. Because there is a lot of human effort spent on, on doing this. So how do we rely on that? 

**Speaker:** It used to be. So remember here we're living in the two thousands, and you're right. So what a lot of companies start doing, start hiring a human labeler. So for example, there is a big project done at Google where they took the, uh, in the, uh, uh, the, um, fundus of the eye to try to identify diabetic retinopathy, and they labeled a hundred fifty thousand labels.

So they used a human to do that. So in the past, we used a lot of human to label the data. Now with generative AI, it's way much better You need to have some quality checks too, and we will get to that too, but it become much easier. This is why in the past you see some of the research where, oh, we did, uh, [00:31:00] um, build a model to predict response on a CT scan, and we use fifty CT scan to do this and fifty CT...

These are not reliable models. But, but for, for those radiology things, yeah, they use a lot of human labeling at the beginning. The same thing where segmentation, for example, like, uh, they train the model to, to segment, for example, the heart and those things. Now, algorithms evolved, so for segmentation, meaning the, the, the algorithm can identify, for example, the heart on the chest X-ray, identify the lung.

The algorithm, uh, improvement also enabled us to make the segmentation much faster and better, uh, and then but still a human needs to verify it. This is why it took a lot of time and effort to do that. With generative AI, what you will see, it's much better now. Um, so what you're also [00:32:00] alluding to is something we will learn in module three, which is called trust, trust of AI system, and that's part of the ethical and challenges that we're gonna learn.

Uh, trust takes time and, uh, need to be earned. So, so we'll talk more about that in, in module three

All right. Uh, I guess this is just examples of, of what, what is, what is, uh, uh... Keep in mind, this is sort of categorical, right? So for example, pneumonia, no pneumonia, that's a binary outcome, uh, prediction. Where how many days this patient gonna stay in ICU, that's a regression problem. So that's the whole purpose of this.

Okay, so let's move to generative AI. So generative AI now-- So we talked about here like more like a prediction for the algorithm. With generative AI is, is really trying to generate something [00:33:00] from something. So a traditional AI task will be what category this belong to, right? So it's like, is this a dog or a cat?

Generative AI, I will give it a cat image and it will transform it for me, or I give it a cat image and it'll make a video out of that. So it's more like generating something from something. So I can give it a text, it can generate a text. I can give it an image, generate a new image and we'll talk more about that.

An example of that, it can generate a document. It can generate evidence-based recommendation. In drug discovery, it can generate a new molecule. It's all AI, uh, generated. So but, but one easy way to think about it, it could be text to text. So you go on ChatGPT, you give it a text, it give you a summary. It give you a question and answer.

It can translate It can, [00:34:00] um, build a new document, summarize all of the stuff. So that's text to text. Could be text to image. You go on ChatGPT, give it a text, it give you... build an image for a giraffe. It will build that for you. Could be text to video. There are many tools now we can take description of the scene, it will provide the scene for you.

Could be text to code, and that's what we have been using now in most of those tools. You, you see, for example, Anthropic saying now eighty percent of the code written in the company is written by AI, meaning humans will just give instructions in human language, and then the algorithm turn, turn that human language into code.

Um, it could be text to audio, it could be image to image, it could be image modification, could be audio to text. So whatever now actually I'm talking is gonna transcribe it using themes. And [00:35:00] most importantly, it can be multimodal. And this is the beauty about this. So multimodal meaning I can give it a text, an image, a video, and it will give me a text.

It will give me an image or give me a video. So I could give images, a text, and I say, "Generate a movie for me." Obviously, we're not at a movie level, but now for video generation, we can generate about like few minutes, and then you can sequence those, uh, uh, minutes together. So y- it's really getting, uh, more advanced in that regard.

So this is why generative AI can be very exciting in healthcare because we are, um, an industry that has multiple modality. So we have the clinic notes, we have images, genomic data, lab results, vitals, wearables, you name it. We have a video of surgeries. So now, for the first time, we can [00:36:00] put all of this data in one system and hopefully get a complete picture of a patient, diagnosis, their journey, where we can predict what they're gonna happen in their health based on all of that data.

This is why this technology will have a significant impact in healthcare if we know how to use it. So- What I'm hoping out of this is if you get out of this lecture today and this slide... You get the slides, like I feel like I got you what you need. 'Cause I've seen a lot of what I call like sometimes mixing and maxing of the terminology because we-- it becomes like too much, the terminologies.

So we need, especially in healthcare, to differentiate between discriminative algorithm and generative algorithm. Discriminative AI is discriminate. It kind [00:37:00] of predict dog, cat, bleed, no bleed, length of stay in the hospital. That's a prediction. Generative AI will be okay. Instead of telling me bleed or no bleed, generate the report of that CT scan, so the whole entire report.

So this is where you see the difference. So anytime now you go, people are talking about a model or talking about deployment, clinical decision tools. What are we talking about here, guys? Prediction or are we talking about generative? And now we start seeing system will have both. Like the model can predict and can also generate.

So let's try to distinguish those together I wanna talk about this because this is, um, sort of become like also big thing in the media now. It started with artificial general intelligence, and people talk about artificial [00:38:00] super intelligence and then what we have today, although there is argument. So, so this slide is, uh, I wouldn't say controversial, but, but the definition of these becomes very controversial.

So you're gonna g-g-get like ten experts in the room, ask them what AGI is. You're gonna fifty different answers. So what I wanna try to simplify it here. So what we have here today, or people argue that what we have today is narrow AI. Meaning, if I have a model that's gonna trained, for example, on a CT scan that has bleed or no bleed, and then I give it a pathology report or, sorry, a path-pathology image, is, is gonna be like, "Oh, well," it's not gonna know that model, right?

The same thing when I was applied to generative AI. It's more like, you know, whatever training data I give it, it's gonna generate that. Where people start going talking about artificial general intelligence, where we start having [00:39:00] machines that have a human-level intelligence across many tasks in terms of reasoning, the machine learning on its own, adapting like a person.

Not... Now, some people argue we already achieved it because the systems that we have in a Claude and, and, and, in ChatGPT, some people argue we're already at AGI 'cause it has general knowledge that humans typically don't have. It can generate different tasks. So if I come to you and say, "All right, find me an expert in, um, oncology," great.

"Find me an expert in oncology who knows, uh, um, AI." Yeah, sure. "Find me an expert who knows oncology, AI, and astronomy." Eh, maybe not that much. "Who knows that and maybe, uh, um, physio dynamics." You're not gonna find that a human. Well, guess what? ChatGPT has all of those. So [00:40:00] this is sort of the argument today.

Are we at AGI or not? That's the goal of those companies because once we reach AGI, meaning that now we have systems that can learn and do things like a human at the level of a human, then we don't need the humans, then we don't need workers. So- Uh, some of those companies like OpenAI and Anthropic will say by the end of '26 or '27 we'll have AGI.

Elon Musk will say he had it yesterday. So again, there's a lot of, uh, talk about this. Now, artificial super intelligence, this is where the machine intelligence surpass human intelligence. Now we're talking about intelligence combine a human being, like the whole populations of a human. Some people say if we continue on the same path, we probably will reach this in about ten to twenty years, and then at that time, [00:41:00] we don't have a human life, blah, blah, blah.

So, so I'll leave it there, but, but I, I put this because you will hear a lot of that, but most people focusing now on AGI and are we there? Are we getting there? And what's gonna happen when we get there?

Uh, I will quickly talk about agentic AI just to stay on time. So, so now we evolved if, if you-- if, if as you see from machine learning, deep learning, where we are talking about discriminative prediction, you know, bleed, no bleed, chest X-ray, pneumonia, no pneumonia, to generative system. That's what we used to call a chatbot, right?

So we'll go on ChatGPT, ask a question, it spit out the question to me Or build an image or build in video. And now we start moving, I would say even in '23, I, I, I build agents in, in '23. Uh, '25 becomes the top of the hype cycle, agents and [00:42:00] multi-agent system. A-and now it's, it's, it's still there's hype behind it, and there's misunderstanding what an agent is.

So, so I hope to, to clarify here and, and in the hope of this course, by the end of the course you build one or you build a team of agents. So this is also tricky because the definition is not universal, and I feel like sometimes people mix things between agents and autonomy. So, uh, you will hear people say, "Oh, if the agent is not operating on its own, it's not an agent."

Well, that's not true. You could have an agent that can give you... For example, go on Expedia website, find information and before it make the reservation for the flight, it discuss it with you without just automatically making that reservation. So autonomy has nothing to do, in my opinion, with agents So, so we need to separate that.

But, but an idea behind an agent, think about it like a system [00:43:00] that can perceive, like can understand data. So when you go to that system, you, you give it instruction, it's gonna understand it. So it's have this perceive. It can reason. So when you give it the instruction, especially for complex task, it's gonna take those complex tasks and kind of like chop them down and also understand, like, what is this task needs to, to, to do and, and sort of come up with a plan to do this complex task.

What separate an agent, in my opinion, from chatbot, is an action. The agent has to take an action, has to develop, has to use a tool to, again, make a reservation, uh, build a slides deck for you. That's an action, right? And now what we start having is systems that can also learn. So the agent can build the slides, go back [00:44:00] and say, "Yeah, I need to modify this, and I need to modify this."

And then you give it sort of some instruction, then it learns the way you develop the slides, and then in future slides use your way or use its own way. So the systems is getting better. There was a recent paper just came out of, of Anthropic talking about this, what we-- they call it recursive learning, and how much these systems now become scary in a way that they learned on their own and then they start improving and improving.

And again, there's some hype to it, of course, but, but also there's some reality. And, and this is where, uh, some of the stuff that we need to, to watch. It's very exciting, but also the capability is moving very quickly. I see a question. 

**Speaker 6:** Hi. Yes, just to, uh, make sure I understand. So, like, ChatGPT, as it stands right now, is an AI agent in that I can give it [00:45:00] a document, ask it to make slides to me, and then tell it to improve the slides with some instruction?

**Speaker:** Yes. It's, it's all of those tools move to become agentic. All of them. Claude. The, the, the, the worst agent or tool is Copilot, but, but all of them, they became agentic. So if you go-- And I will show you when we talk about the tools, how it's think, plan, execute. That's, to me, agentic. It's not a chatbot anymore.

So to, to that extent, yes, you're correct. All of them become agents, basically. So this is just to kind of tie it up to your question. So what does make it an agent? It's now, depending on the tools, you have the capabilities of connecting ChatGPT, for example, to multiple tools. And that give it a lot of power.

So I can connect it to my Google [00:46:00] Drive and my SharePoint so it can extract the information. In fact, today I can connect it-- connect, for example, Claude to my desktop, and I connect it to a folder, and I can, in the prompt, say, "Go to that folder, find this lecture, add slide number five on this lecture," and it will go find the lecture, add the slide, and then push that lecture back in the folder without me going and uploading and doing all of this stuff.

You can connect it, obviously, to the EHR. You can connect it to, to pay your bills, uh, to your credit card, and that's the beauty of this. I can connect it to a hundred tools. It also has memory. So if you go on ChatGPT, it has short memory. So short memory meaning it's gonna remember the previous prompt. So you have this chain of prompts, it's gonna remember that.

But also now it has long memory, and that memory is getting bigger and [00:47:00] bigger, which is, which is important. Long memory meaning it's gonna remember previous prompts. So if you go on ChatGPT today, sometimes you feel like, "Oh, it's kind of sneaked in some of the information from previous, uh, prompts." What, what they're trying to do is trying to personalize the, the outcome and the output, so sort of remember some of your style, your situation, and kind of answer that.

Uh, and sometimes becomes annoying because you don't want it to use that. So you could either tell it not use it or go and shut down what they call it the long memory. What I will show you now most of those system, if not all of them, they have a planning and thinking and skills. And the skills is, is like sort of a set of instructions that the system use to complete a task.

It can retrieve information, so if you upload a PDF document, it's gonna dissect that document and extract that information. You could [00:48:00] point it to a SharePoint or a set of documents and extract that information. Some of those systems in a multi-agent system, it can delegate, meaning you have an orchestrator agent, you have a small sub-agents.

The sub-agents can perform a task with this tool. The sub-agent can perform a task with this tool. The orchestrator agent come up with a plan, assign it to the sub-agent. Those sub-agents go execute that small task and bring it back to the master agent or the orchestrator. I'll show you that how it works in some of the tools.

And also we have some, some guardrails. If you go today on ChatGPT and say, "Help me build a nuclear bomb," it's gonna tell you, "No, I'm not gonna help you." Or, or if, if you wanna, for example, do like a, a sha- uh, shady things. It's not... So, so there are some guardrails. However, there are ways to get around those [00:49:00] guardrails, and that's what we're gonna learn in module, uh, three This is what I was talking about, the multi-agent system.

This has evolved, by the way. It's just the last two months, it's, it's getting crazy how this stuff is changing. If I'm giving you this lecture in December twenty twenty-five, ninety percent of what I said now would have been different. So it's crazy. But, but you see now this multi-agent systems where you have an orchestrator agent, as I mentioned, and some sub-agents that can perform a task.

The orchestrator agent come up with a plan and then assign it to sub-agents. Anthropic has a different thing. So instead of using agents, they use what they call it skills. So set of instruction. Nobody knows, at least to my knowledge today, because this is new, a multi-agent system is better than skills. In my experience, [00:50:00] depend on the case.

Some cases, multi-agent system is better than skills. In some cases, skills is enough. You don't need multi-agent system. We'll dive deep into this stuff in module four because this is really becoming like deeper and deeper now we're going into the technology. And again, this, this sort of evolving every day, new techno-- new terminology coming.

So you have agentic workflow versus agent versus multi-agents versus skills and, and I can have like ten other slides of some of those, um, terminologies. But to simplify, you could have what we call it a workflow. So you have agents, you don't need one. You can have a team of agents, and then you build a workflow where some of the tasks are done by agents, or some of them can be done by human, and some of them can be done by [00:51:00] both, or the entire workflow can be done by agent.

But then it's sort of more like structured. So the first agent will do this, the second agent will do that, the third agent will do this, and then you run the workflow. That becomes an agentic workflow. A single agent, again, you can build an agent, you can have data On a specific topic and point that agent to that data.

So let's say you want to build an agent that can help you, uh, answer questions about HR in, in, in, in Jefferson. So if you have a question about your benefits, what you will do, you take all of these HR documents, let's say benefit documents, and you point the agent to them to retrieve that information. So if you go and ask, you know, "What is my four oh one K matching?"

And those things are gonna go to that document, extract this information, give it to you. That's a single-agent simple. We call it RAG agent, [00:52:00] retri-retrieval augmented, uh, generation agent. That's very simple agent. Multi-agent system, as we discussed, you have multiple experts working together, uh, and trying to complete, uh, a broad and complex task So, all right.

Let's, um, let's see if, if this resonate. So, uh, an AI that flagged diabetic retinopathy in retinal photograph, is that generative or discriminative AI? Sharol. 

**Speaker 6:** Discriminative. 

**Speaker:** Great. An AI draft a discharge summary from patient's chart 

**Speaker 3:** Generative. Generative Right. AI 

**Speaker:** predict thirty-day admission risk as high versus low.

**Speaker 3:** Discriminative 

**Speaker:** Eight. An A- AI designs a brand-new [00:53:00] molecule to bind to a cancer target. 

**Speaker 2:** Generative. 

**Speaker 6:** Generative. 

**Speaker:** An AI answer patient questions about their medication in plain language. 

**Speaker 6:** Generative 

**Speaker:** Yes, that's generative AI. Perfect. All right. Now, um, well, I wanna keep with my promise, and, and this took, uh, longer than I thought.

Okay. So we can take a break. What I have here is, is sort of some of the literature that has generative and discriminative AI in healthcare. We can go through that quickly, or what I can do, I can share the slides with you guys, and then we will take a break now, and then when we come back, we'll, we'll visit the tools.

So why we don't take a break now, a- and then when we come back, we'll decide whether we wanna visit the tools or quickly review this literature

**Speaker 2:** Sounds [00:54:00] good. What's the break? How long? 

**Speaker:** Uh, let's do 10 minutes. 

**Speaker 2:** Okay. Thank you 

**Speaker:** all right. Uh, let's get started again. Um, so what I think we will do now is, if it's okay with you, just for the interest of time, I will, uh, send you the slides that have the second part of, of the, of these slides. Wh-which really... Let me just show that, uh, share it with you because I wanna move to the tools, and I promise you we'll leave in an hour and a half.

It looks like we're gonna spend an extra half an hour in the class, which, which I don't wanna want you to do. But, uh, so it's really just describing some of the literature and how it's applied in healthcare and then, uh, some of those references basically. So what I can do, I can send you those, you can read them, uh, some of those papers, and then if you have any question, obviously, we will [00:55:00] discuss them, uh, during the week if y-you can email me or, uh, next time when we meet.

But, but if it's okay with you, I would like to go to talk about some of the tools, uh, in the next, um, probably thirty minutes. Show you what are those tools, and then show you some of the differences between these tools. Um, it's gonna be really hard for me to show you all the tools, all the capabilities, and I'm gonna focus on some of the tools.

Notice here I don't show you Copilot because I don't think it's a tool, to be honest with you, but I wanna show you the other stuff and how it's, it's evolved. So there are other tools that can do video generation, uh, can do image, better image generation, those things. I will not be discussing those tools, um, but we can, we can talk about them.

So, so the most common [00:56:00] ones that most people are aware of, obviously Copilot one of them, but Claude now become sort of more in the m-media, and I'll show you the difference. ChatGPT... For consumer AI, ChatGPT remains number one. For enterprise AI, Claude is number one now, and Claude is, is getting bigger market share, uh, as we speak.

Google has Gemini And, um, I like Gemini, although I mainly use Claude now and ChatGPT. Uh, there is really interesting tool from Google, which is NotebookLM. I think this is-- If you're doing any sort of a research type or, or anything, this is a great tool. I, I wanna show it to you. Um, Manus is one of my favorite tools.

Um, and, and, and we [00:57:00] did a lot of surveys in, in, in Jefferson asking people familiarity with the tools. A lot of people just don't know anything about Manus. I think it's an amazing tool. I'll show you that. And 

**Speaker 3:** then- Who makes Manus? Who makes Manus? 

**Speaker:** So Manus was a company in, in Singapore that was bought by Meta last year.

**Speaker 3:** Got it. Okay. 

**Speaker:** Yeah. Yeah. Manus is, is amazing. To be honest, Manus was the first one sort of got to the agentic world even before the other tools. Uh, it... I mean, big story, but it used to be a Chinese company, and then they moved the headquarter to Singapore, and then Meta bought them last year. So now they become- Did you say- -part of Meta.

Yeah. Sorry. 

**Speaker 9:** Did you say Claude is for enterprise level? Claude is the best. It's not. Didn't we-- Weren't we told not to use anything but Microsoft- [00:58:00] Yes -Copilot? 

**Speaker:** Yes. Yes. So all of these tools 

**Speaker 3:** you're 

**Speaker:** not allowed to use 

**Speaker 3:** at Jefferson. Yes. Uh, un-unfortunately, that is the, the point here. Like right now, uh, you know, we are not allowed to use these tools for Jefferson related data or anything like that.

But, you know, they are working very hard to begin to get these into the system. It has to go through like the IC- ISNT process to put the BAAs in place and MSAs and all the above. So we're moving towards it. It's not there yet. But do not put any Jefferson specific data. We, we can play with these tools. I use them all the time.

Everyone knows it. But I u-- I, I don't put anything Jefferson specific into these systems at this point. You cannot do that. 

**Speaker:** Yeah. It's, uh-- That's actually what I was trying to get to. Sorry. So these tools, anything is public, don't... Any, anything you put on those tools is public knowledge. So you, you shouldn't be putting it on these tools.

What I'm trying to do here is to show you where the tools [00:59:00] are. To be honest, Copilot is a little bit behind now. So if I show you Copilot- A, a lot 

**Speaker 3:** behind. He's, he's being nice. It's a lot behind. 

**Speaker:** I'm, I'm, I'm trying to be nice, yes. And not trash Copilot and Microsoft as, as the worst company in the world, but yeah, uh, it's way behind.

It's like, uh, it's like, you know, again, driving, driving Camry nineteen sixty and then the tools I'm showing you is just like the Tesla Plaid. You know, Model S now compared to that-- to Copilot. So I'm trying to strike a balance between showing you the tool where the technology is evolving and the agentic stuff.

But at the same time, we have to stick with Copilot. The organization is working on Claude license. Um, but, but it's taking some, some time just because now it's impossible to talk to Anthropic because now Anthropic valuation is about a trillion dollar [01:00:00] now. So they, um, they just raised a new, um, funding, sixty-four billion dollars funding for a valuation of nine hundred fifty-four billion dollars for a company that make about forty billion.

So yeah

**Speaker 10:** Hi. I wondered if you, um, could speak to the Hippocratic AI program that they're-- they use in documentation with Epic. 

**Speaker:** Yeah. So, so I'm not gonna be able to talk about those tools. That one is more like a sort of a patient-facing tools. There are some of the tools in Epic. What I wanna talk about here, just show you some of the capabilities of the tools.

Uh, trust me, I can spend month and month showing you tools and capabilities, and some of them at Jefferson, some of them outside of Jefferson. It's just gonna get out of scope. Uh, number one, giving this seminar and workshop multiple times now, what I [01:01:00] learned, it's a little bit overwhelming . So I'm trying my best to simplify things and not make it overwhelming as much as I can, but it, it's, it's a lot.

And the other problem with those tools, they move so quickly. So if we have done this in January of this year or February of this year, whatever I'm telling you today is, is, uh, is gonna be the opposite. I would have been on ChatGPT, and I wouldn't tell you that the Claude is good. And, and half of the capabilities that I'm gonna show you here did not exist in February.

What I'm trying to say, the technology is moving so quickly, it's just, like, hard to keep up. What you will discover from those tools, couple of things. One, each tool has its own personality and own strength, so I encourage you to play with all of them and then pick up one or two or [01:02:00] three if you want. Uh, but each one has a different personality, different capabilities.

Personally, I find ChatGPT still the best in creative work and brainstorming and learning. I find the Claude is the best in doing work for me, slide generation, uh, like doing actual work. NotebookLM is excellent if you're doing research, gathering information, put it all together in one place, search that information, build the questions, build the stuff.

It's great. Manus, it's great in building websites, application And Perplexity is my favorite one for data analysis, literature review, and research. 

**Speaker 3:** Can, can I say one thing about NotebookLM? It, it is a- Yes ... a great tool in general, and [01:03:00] it take, it can take a lot of information and actually turn it into, like, a podcast.

You can throw, uh, uh, documents in there and, and, you know, say it's a big article, a journal article. You can literally throw it in NotebookLM and tell it to turn it into a podcast for you, and it will turn it into a podcast for you. You can want two people talking, three people. It, it's a, it really is an interesting tool, so that's one that's on the radar, but very interesting.

**Speaker:** Yeah. Thanks, Keith. And they add more capabilities. Uh, so, so since you talked about NotebookLM, let's talk about NotebookLM first. Uh, so, uh, so if you go on NotebookLM, I, I pulled up one. So, so let me show you this. So, so these are notebooks. So think about a notebook, as Keith was saying, where you can gather information together.

The free version allow you to put fifty documents. That's can be a document, can be a YouTube video, can be sort of, uh, audio and, and that's the [01:04:00] beauty about it. So for example here, you see somebody built this where it's a AP course refresher world history modern. So what they did, they added all of this text here, and what you can do, you can ask questions and extract that information from those documents, and then you can build sort of a guide.

It help you build e-exam questions inside the studio, uh, flashcards automatically. So again, for, for somebody who's doing research and education, it's a great tool. So let me show you how does that look like. Um- So this is, for example, a, a, a video that I gave about personalized prediction models in MDS. You can take that video.

What it does, it take, it take it and transcribe it, and then you can ask it questions. And here you can start [01:05:00] building this stuff. So you can build a slide deck, and what it does, it take all the content here and build a slide deck for you. It can-- Now they added this video over, uh, view so you can say, for example, this one, and it, it build.

Let's generate one. It takes some times. It can build reports. It can build flashcard, automatically build a quiz. So again, if you're teaching a course, you take that, you upload all the course materials and hit quiz generate, and it will automatically generate. Uh, it will generate infographics. So let's generate some of them.

Takes some times, but, but for example, I generated this infogram, infographics

Uh, let's see. 

**Speaker 2:** This flashcards?

So that's for education So they keep adding capabilities. 

**Speaker:** This is a quiz

[01:06:00] Yeah. See, this is how I scored high on the exam, just by not knowing the answer. I got this wrong. But, but this is what, what, what, what it does. It's very beautiful tool to organize your research library in a topic. It's free. Don't put Jefferson's stuff on it. Meaning, don't go and put, like, Jefferson policy to organize them in one place.

Put research articles to organize them in one place. 

**Speaker 11:** Can you-- Do you have to put s- um, pu- copy and paste all of the text, or can you just prompt it with the citation? 

**Speaker:** Ye- So what you do, see here, you can add a source. So either you search for the source, you upload the file, you upload the web- the, the website or the video, or you connect it to your drive, or you can copy and paste text.

So if, if I wanna search, for example, [01:07:00] uh, this does have personalized diction model in MDS GSCO. So this is one of the paper. So

So it's gonna go find that website, or you could go and find... See here, it's found the website. So this is sort of Some of the stuff. So I can say I wanna include this article that I published. I wanna include this, for example, and then I import them, and now these articles are already there. This one, for some reason, didn't pick it up, but this one, it picked it up.

So I can then go and say summarize the, uh, personalized prediction model JCO paper. Thank you. And then you can extract that information. You can build, uh, new data from it. This is the summary of it. 

**Speaker 6:** Excellent. Can it [01:08:00] also connect to, like, your, like, online citation manager, like Lean Library or SciWheel? And, like- I 

**Speaker:** don't think- I don't think so, but you can...

What I found, to be honest with you, I stopped using those tools. When I write a paper, I ask it to put the reference at the bottom. Actually, Perplexity is the best in putting the reference. And then when it put the reference, what I will do, I will upload the manuscript and say, "Change the reference fi- ba-- to match this journal citation," and it will change it for me.

So I don't use citations tools anymore

Um, maybe we should jump to Perplexity. So what I like about Perplexity, uh, is first of all, all of them, what you're gonna notice, they have sort of the same, um, user interface. You have [01:09:00] all the stuff here. Some of them, they call them projects. In some call it spaces. You have search capabilities in all of them.

You can upload files or drag the files to the tool. And what you start seeing in those tools is what we call it connectors. And connectors is where you connect the tools to the stuff, uh, that you want it to be connected to. So for example, you can connect it to your Drive, you can connect it to your SharePoint, you can connect it to a website, or you can connect it to a tool.

Salesforce, you can connect it to a registry. Uh, again, you're not allowed to do any of Jefferson's stuff on these, uh, things, but for example here, you could connect it to your Google Drive or OneDrive or SharePoint, but not for Jefferson stuff. Dropbox or Box. Computer, it's, [01:10:00] it's, it's the Sort of what we call it now, co-work on a cloud.

It's called Codex in, in, in ChatGPT. And then the idea here, this is to me the actual agentic framework. Meaning that this is gonna be connected to multiple places, it's gonna extract information, and it's gonna plan and execute task on its own. I cannot show you computer. So computer, you need to have a pro plan, meaning you have to pay more, so it's not a free plan, and this is will do actual work for you.

I cannot show it for you because I max out my credits, but I'll show you something similar to it. And then it has this Opus, uh, uh, you can choose the model or Perplexity choose the model for you. 

**Speaker 3:** I'm sorry- We will be- Perplexity is connected to cloud? 

**Speaker:** Yes. 

**Speaker 3:** Oh, cool. Okay. 

**Speaker:** And then it has orchestrator, and it kind of like pick the [01:11:00] model on its own.

**Speaker 3:** Got it. 

**Speaker:** And then they have the Fablay Five, which is just came. These, we gotta talk about these models in the next week. So for now, it's okay if you see those models, they don't make sense. We'll talk about them more for next week. But I wanna show you what I have done with this, which is research, which is data analysis.

So I took this data set, and I give it a prompt. We'll talk about prompt. You're a senior biostatistics trying to identify, uh, some questions, uh, in terms of survival for patients with myelodysplastic syndromes. And then what it did for me, it's kind of I used computer for this, but you can use it without computer.

Kind of looked at the data, understood the data, developed on its own the statistical analysis plan, and [01:12:00] then- Delivered this plan for me. So it has sort of the table, the descriptive table, the cutoff for the blast, and build the Cox univariate, the Cox multivariate survival analysis. And I start asking it questions, and it start building the data, start building the analysis and the graphs, and I could download the entire, like, um- 

**Speaker 12:** Sorry

**Speaker:** analysis. Not to say that we don't want statistician or we don't need statisticians anymore. I can tell you it's pretty accurate. Now, you have sometimes to verify. It's getting much accurate now, but you have to verify the information. So what I do... You know, all of us, sometimes we have, like, ideas to do research, but [01:13:00] sometimes we just don't pursue them because we don't know if that idea gonna yield something.

So think about this like brainstorming, quick, dirty analysis. So now doing this analysis like, "Oh yeah, this is actually looks interesting. It might get me something." Now I can go and do more detailed and better analysis, but, but it, it, it build correlation, it give me all the abnormalities, it give me new classification for myelodysplastic syndromes.

Um, there are some stuff I agree with. There are some stuff came up with it's like, "Hey, this is not what I want," but, but look at me. It build this survival data, show it clearly. Uh, build this Co-Cox model, which is correct by the way. How I know? Because I know this analysis is done. Show me the cutoff and, and show me the hazard, and show me the impact of some of the mutations and those things.

So it did a great job, I can tell you that. Uh, [01:14:00] let's see. How much time we have? Okay. Now... So to summarize, I like Perplexity for research work. It's great in literature review, so let me show you something here. So I did this, um-

A scoping review on AI in healthcare systems. So what I ask it to go and build a review article for me. Uh, so you are a AI researcher. Build a scope review to answer questions. Uh, so there was a editorial board question about is there an impact of AI in healthcare? And the argument was, yeah, there's a lot of research, but today, in terms of impact, in, in terms of money saving, productivity, blah, blah, blah, there's no documentation for that.

So for example, we can deploy ambient listening in hospitals, but there is [01:15:00] no study that have demonstrated an impact on patient outcome or an impact on, let's say, uh, increased productivity. Most of the studies have shown it improve, uh, uh, uh, p- physicians' burnout, uh, maybe decrease time, maybe not. So what I ask it to do is to do that.

And it-- what you see here, that's what I was trying to kind of talk about in the lecture where it come up with a plan and it start executing the plan, basically. And what, what... Again, we will run some of this stuff. You can see here, it's for the... First of all, it read the Nature Medicine editorial And then took that editorial, and then they-- it, it sort of couldn't access the full thing, so it start trying to find other information about it on its own.

And then it start actually le-- uh, running skills. So it hired two agents. One has the [01:16:00] skill of research assistant and one the skill of research report, and start building

The plan, which is draft the perfect prompt, because I ask it first to write the prompt for me, 'cause I'm lazy, I don't write prompts. Second, run targeted literature. That's on its own. I didn't ask it to do that. Build an evidence table, analyze the attribute, and compare academic health system versus community practice.

Then it went and start writing the document and pulling up the prompt. Long story short, after I got my cup of coffee... Uh, I wanna show you. I ask it to add some stuff. Ah, yeah. So, uh, so this is the paper that it came up with

It wrote the abstract, the conclusion, the background, objectives, method. It used the PRISMA method to do that, analyze all the data, give me tables, [01:17:00] and it has the references And this is another tables, and I ask it to build also images for me. So it build a nice image repository. Uh, then I ask it later to build the image.

Okay. Then I said, "Look, I wanna submit this to New England Journal AI." So, uh, no, before that, I, I said, uh, Nature and Medicine. "So go find Nature and Medicine requirement, rewrite this based on that requirement." So it did that As a short report, and then it took the other information, put it in supplementary tables.

So you see now it's more like a nature, what do you call it? Quick evidence or something that style. You know, and it's put the images at the end. Figure, figure, figure, and then the tables. And then took the extra information that couldn't [01:18:00] sneak it in, in the paper and put them in supplementary information.

And I read the paper. It was, was pretty good . So I need to make some tweaks and then think about submitting it if I wanted to So this is what you can do with this. Um, maybe we should jump to Claude to show you how Claude works. So, so here what I wanna do is show you-- We're gonna talk about the models.

They just came up with this model. Was it ye- two days ago? It's hard to keep up. This is now it's taking the top chart of the models, and by the way, you don't have access to it un-unless you pay. So the free plan, it, it's kind of kick you out quickly, then you go to twenty. I pay a hundred bucks, uh, because I do a lot of work on, on, on this.

Uh, so let's say you are an AI educator at a university We'll learn [01:19:00] prompt engineering next time. Build a slide deck, uh, to-- for in-introduction of AI in healthcare. See, I didn't give it anything. This is about a prompt which we will learn, but I wanna show you how-- wh-what does agentic mean, and how it's different between tools.

So Claude use what we call them skills. And skills is a set of instruction. So let's see how that pan out, and I'll, I'll show you. So, so now it start working. So it start thinking. Now you can see what it's doing. So first, it's trying to understand your question. This is what we talk about agent, right?

Receive the information, understand the information. It has the skills in the file. So the first skill it build, uh, it took, it's [01:20:00] how do you build slides on PTTX? This is the skill. And again, the skill is a set of instruction

Read from scratch creation guide. So it's planning out the... So again, this is sort of where we talked about the reasoning and the planning. Then it checked installed packages, and then for the style, it needs to install this package to build the slide. So it's doing that. It's setting up the color. I didn't ask it anything.

By the way, you can take, for example, like a Jefferson template and ask it to do it on Jefferson template. It will do a great job on Jefferson template, but you're not allowed to do that because you're not allowed to use it. But if you wanted to use a template, it can do that. Now, what you're seeing here, it's building the slides.

**Speaker 2:** Building the slides. 

**Speaker:** And what it's doing, building the content and the style

Any [01:21:00] question?

**Speaker 2:** Oh. 

**Speaker:** All right. So let's see when it's finished. So, so this is what, again, I-I, what we discussed about agents, right? It's perceived the information, it's planned it, picked up the skills. You can also-- We can talk about that connected to tools. So we might go and co-pick, pick up the tool, and then now it's performing an action on your behalf.

You go, you make your cup of coffee, you come back, and the work somewhat done. Now- What we will learn is that this is a bad prompt. So for it to get better outcome for us, we need to be more specific, and that's what we're gonna learn in the next, uh, uh, next time we come together. But, but this is also the same way it builds software in, and that's what we discussed in the [01:22:00] class, right?

I give it a text. What you see here, it's turning that text into code because what it's doing here is you-- is doing HTML, which is a language that build website. So the way it's building the slides first is building in them as HTML pages, 'cause the style is easier on HTML. And then now it's gonna take them and turn them into PowerPoint slides.

So it's not filling them on the PowerPoint per se. So now is, is, is looking... Oh, I can't load that And it's adding question slide one, question slide two. It's reading slide three in, in C

You can see some of those images in the slides as it's reading it on its own

And reading. Again, I'm not doing anything, but, but I wanna show you how this evolved the thinking and [01:23:00] where, you know, sometimes you hear on the news that, "Oh my God, this stuff can do work." Yes, can do actual work, uh, and has the skills to do that work. Now, as it's cooking here, I wanna show you the difference between Manus and this.

Because what Manus does, it's-- it doesn't use the skills per se, but it use sub-agents. So, so we can just for comparison, take this. And what you will notice working with those tools, you can take the same prompt, put it on different tools, you will get completely different result. So this is why I encourage you to play with them and then find which one is your like.

So here, for example, see now it start thinking. And after it's thi-think, it start coming up with the plan. So Manus, the way it does it, come up with this plan. So see, it's... So the first thing I need [01:24:00] to research AI in healthcare topic, then I need to write the structure slide, generate the slide and then deliver it.

And you can see what it's doing here. So what it's doing now is going through doing the research. So these are the papers that is researching that. So it's researching the papers. Basically going to the internet to research the information, find the information. Now it's writing the structural slide content.

So it's finished the resea-the research. Now it's writing the content

**Speaker 2:** And you can again watch it here doing that work

**Speaker:** So we'll go back to see if, if, if Claude finished. So Claude looks like it finished. All right, so this is the slide presentation. For some reason, it has a bug that doesn't show it here, but, but let's open the slides. You can download them, and you can [01:25:00] open them

And these are the 

**Speaker 2:** slides

This is the style that choose

And it used some of the, um

**Speaker:** Audrey O's. Again, I didn't give it instruction. Beautiful slides. Like how long it's gonna take me. So if I give it the content and I say, "Just do the style for me," how much time this will save me, right? Uh, let's go back to Manus. So Manus is still working, but, but you get the concept here, right? Come up with a plan, stop agents or skills, go execute something for me.

And this is the power of these tools. It can build a website for you, and Manus can build an app for you. I'm using Manus for free, but also it's, it's probably what happened with Manus sometimes it's gonna kick me out now because it say, "Oh, you're now out of credit. Pay me money 'cause you're using a lot of compute."

Um, ChatGPT now on [01:26:00] the, uh, sort of if you look at it, it has the same capabilities. Uh, you... Now, um, I can show you what we call it agent mode, but the idea behind agent mode is, is what you saw somehow on, on, on, uh, Claude and those things. It will go and do task. But the difference with agent mode, which, which Claude Cowork has, is that it can access websites and it can click on the websites.

So for example, I ask a Claude Cowork, which you have to download on your desktop, to go on a abstract website for a meeting and click on each abstract and extract that abstract data and structure it in a table for me. And it went and it did that. So I don't have to go and click on each abstract and, and do that.

[01:27:00] So, so that's, uh, you can do with agent mode, but I don't have that here. The other thing, although now it's kind of start getting less, is when you put the model on thinking, it will start doing more planning and thinking. So this is supposed to be for complex task. It used to be you can put those on thinking, and just this week they took the thinking out, and then they changed that on a Claude.

And this is why what I was trying to tell you before, like probably in two months, whatever I'm showing you here will be outdated. And more capabilities and more models gonna come and, and, and, and take-- it can make big difference. So- I know this is a lot, but what I am hoping is [01:28:00] if you can just start playing with this, not on Jefferson data.

Please don't use any Jefferson data, just stuff that you, you, um, you know, working on your research or, or, or something you wanna do, um, like a research a topic or learn about topic and start using different tools. You might not get the full capabilities if you're using them for free. And I don't just suggest also that you pay twenty dollars for each one of them.

But maybe if you like a tool, try also to pay because it might give you a little bit more than just the generic one All right, so let's go back to Manos. Looks like it, it, it put the slides in in here. This is Manos' slides, and, and you see it's different slides

That's why I like now most recently-- [01:29:00] So again, in January, I would have probably used Manos. Today, I, I'm using Claude for slides. Obviously, you can give it the style and those things, it becomes better. Uh, but, but, but this is just to show you some of the differences between tool. So I wanna pause here, get some questions from you guys

George? 

**Speaker 8:** Yeah. Hey, it was-- it's great. I, I love seeing all these tools in that, uh, you know, I, I sorta feel like I was a quite early adopter of, uh, you know, ChatGPT. Um, and I just wanted to know just real quick on your insight. You know, I've used, um, a lot of ChatGPT just for sort of scheduling algorithms, you know, for our sort of staff.

Um, kind of also just looking at balancing of kind of calls and shifts and stuff like that, and kind of doing kind of retrospective reviews and stuff like that. And then, you know, last year I kinda put in our holiday grid of sort of holiday requests to [01:30:00] see balance that out, you know, sort of in a more instantaneous way.

What platform would you use for that? And just kinda looking at all these options, 'cause, you know, there's even some that you threw out there that I'm just not as familiar with, for, like, those kind of analytics. 'Cause I know you said originally, like, ChatGPT you look at as more the creative side. So I might get better results by using a different platform.

So if I was gonna try and rerun those algorithms, what, what platform- Yeah ... would you suggest for something like that? 

**Speaker:** Uh, Claude. 

**Speaker 8:** Claude? Okay. 

**Speaker:** Yeah. Recently. Recently. Just- Um, five point five-- So ChatGPT five point five is good. If you download Codex, which is part of that, it will do much better job. Uh, if you're-- You're paying the twenty bucks on ChatGPT?

Yeah. Yeah. So it'll give you more stuff. But, uh, so I was like you until February, and then I completely one hundred percent switched to Claude recently. Interesting. [01:31:00] Yeah. I shouldn't say that. I lied to you. Most of my work on Claude, but, but for research I do Perplexity. For, uh, specific type of work I still do ChatGPT.

For, um- Some of the work I do matters, and then for app building, I do base44, which we didn't talk about because again, I don't, I don't wanna overwhelm everybody. But how do you build an application using just text? That's, that's what I use is, is base44. Some people use Lovable, some people use Replit, and there are so many tools, but I prefer base44.

So as you work with those tools, as I mentioned, you see different personality. I can show you. I can take the same prompt pro- put in each one. A different answer, different personality. I found ChatGPT is a little bit now manipulative, meaning it's gonna tell me what I want to hear. I found the Claude is more [01:32:00] direct and sometimes a little bit like, "Hey, man," it's like, "You're hurting me now."

It's like, "I'm gonna be direct to you." I was like, "Whatever." And 

**Speaker 8:** then one, one other quick thing. If I took the code... Sorry, Keith, didn't mean to cut you off. If I, if I took the code out of ChatGPT and dumped it into Claude, will it clean up that code? So- Yeah, it will ... so is that a good place to start, or do you start over?

**Speaker 3:** So what you do, I, I was actually just gonna comment on that. So, um, Claude built actually provides a prompt that allows you to take all of your chat history into Claude, and then, you know, so it'll have- Mm-hmm ... your stuff literally from day one. Each time. And then you can start over. 'Cause I was, like Aziz, I used to use Claud- I mean, chat a lot and then switched it over to Claude.

But Claude literally has a prompt that you put in there, pulls your history. You take that prompt, you put it in chat, it pulls it together, then you have a prompt that you put in the Claude, and it pulls everything in there. So it can actually, you know, it, it'll remember everything that you did from, uh, from chat.[01:33:00] 

**Speaker 8:** Very cool. Thanks. 

**Speaker:** For, for coding, Claude is number one. No que- nobody argue with that

Santa? 

**Speaker 13:** Uh, yeah. Thanks, Aziz. A, a great presentation. I just wanna make sure I'm, uh, you know, complying with, uh, organizational policy. When, when you, when you say that we can't use, you know, put data in, into all the, you know, Claude and all that kinda stuff, can we at least download these programs and use them with, uh, as long as we don't put Jefferson data on our Jefferson laptops, or do we do...

or, or we have to use it on our own personal computers? 

**Speaker:** Yeah. So all of them, you cannot download these. You have to use them through the internet. And once you do... So, so let's say you have a dataset, um, you are not allowed to put it on those tools, so Jefferson dataset. So the, the research that I showed you, this is publicly available dataset that I was playing with it.

But let's say you have a patient from dataset from Jefferson, you cannot upload it [01:34:00] to any of those tools. 

**Speaker 13:** Right. But, but, but for instance, if, if, if I wanted to u- use... So, so I can use Claude on a Jefferson, like, issued computer? Yes. Uh, okay. Yes. That's my, my question. Yeah. Yes. 

**Speaker:** Okay. That's what I'm doing now.

**Speaker 2:** Yes. 

**Speaker 13:** Oh, okay. Okay. So, 

**Speaker:** so we didn't block... There's a big conversation about blocking those tools. We don't wanna block them. We want people to, uh, be aware of them, but we also wanted people to be responsible, that not using any Jefferson related data in those tools. 

**Speaker 13:** Okay, great. 

**Speaker:** Yeah, yeah. So I'm using my Jefferson laptop to show you all of those tools.

**Speaker 13:** Okay. Thank you. 

**Speaker 12:** Me too. Hmm. Great

**Speaker 7:** Um, I had a question regarding the app building which you mentioned. Um, would you like to just show or a little elaborate on BASE44? You know, app building is crucial these days, particularly if you are trying to do any research which is patient-facing. You know, you wanna build an app, you wanna send them the patient-reported [01:35:00] outcome questionnaires, get the responses back- Yeah

and then have a, you know, provider login or a, you know, project coordinator login where they can follow those prompts. A little bit more on that would be helpful. Thank you. 

**Speaker:** Yes. 

**Speaker 7:** Wonderful 

**Speaker:** talk. So, yes. Uh, so I'm happy to show you that, but also you're not allowed to use that app building to do that for patients at Jefferson.

You can build an app, let's say, to, to do some, some stuff, but, but to be able to use that app on Jefferson data, uh, you have to sort of take that app, deploy it in Jefferson environment, have all the security around Jefferson environment, which we're not, we're not doing that yet. The-- I, I think Jefferson's gonna try to think about building those apps internally.

So the short answer, if you're trying to, to do that with patient interfacing and sending all this information, you are not supposed to do that. If you're trying to build an app to, uh, um... For example, I built one to [01:36:00] generate board questions for me and, uh, you know, I can give it the topic and generate the questions and then score me and then, then give me answers.

Yes, you can do that, I mean, because there is no Jefferson proprietary information. I'm not using it to make any clinical decision tools or anything in my research. You could try Manus first before you go to the other ones. Um, if you-- I give you another example I did recently. It, it was in the ASCO meeting, the American Society of Clinical Oncology.

I took the abstracts, download them, uploaded them, and I said, "Build a dashboard for me that explain all of these changes." And then I ask it to take, just focus on AI topic and show me, like, what are the most common ones, organize them in topics, do all of this stuff and build the dashboard. And it built the dashboard, and I published it, and then I started like, oh, clicking on it and go from study to study.

So that's ano-another way you can do it [01:37:00] on, again, publicly available datasets, has nothing to do with Jefferson. 

**Speaker 7:** And, and you used Manus for that? That, that is really interesting for, for 

**Speaker:** us. I used Claude. I used the Claude for that. 

**Speaker 7:** Interesting. Yeah. Okay, 

**Speaker:** cool. Yeah, I keep going to Claude, uh, for now. But, uh, Manus, Manus, I, I tried to build an app on it, and it keep kicking me out because it say I, I n- I need money.

And then the computer on Perplexity I used too, and then it kicked me out. It's like, "You're running out of credit. Pay me more money." I was like, "I can't do this. I'm running out of money." Uh, Darren? 

**Speaker 14:** I know we kind of talked about, you know, how Copilot is definitely, you know, far and away behind everyone. Is there anything you actually have been, you know, putting Jefferson data on to actually use in your work?

Um- Yeah ... 'cause by the sounds of it, we can put Jefferson data into Copilot. Yeah. But like any use cases, just [01:38:00] quickly. 

**Speaker:** Yes. So, uh, and we should have talked about that. So Copilot, you have two Copilot. One is the generic one that's available for everybody, and then you have Copilot with the three hundred and sixty-five-- they call it Microsoft three sixty-five Copilot.

That's a license that we pay for. It's about thirty bucks. On the three hundred and sixty-five, the good thing about Copilot, to be honest with you, uh, uh, is, A, it can integrate with, with, with your email, it can integrate with your SharePoint. So what you can do, uh, what I do with Copilot, uh, if you have the license, uh, I can, uh, go and say, "Okay, this week, summarize all the meetings that I have and help me prep from my..."

And it go and kind of like go to your slides and say, "Maybe you should use this and that." I use it for data analysis, and I think it's okay. And then number three, which is important, [01:39:00] Copilot gonna bring Claude Cowork to Copilot, and it's in, in, in beta now. They said in the next few months they will start releasing this.

So when it's that released, I think that will improve the capabilities of Copilot. So, so it gonna have some Claude capabilities hopefully soon. And once that happen, then it makes it easier for people to, to kind of jump to Copilot

**Speaker 2:** Thanks. 

**Speaker:** And it's good in slides. Not as good as th-those ones, but, but also fill up the slides and directly put them in PowerPoint, and then you can edit them. So I've, I've used it for some slides too, and it, it's doing good job. Uh, but not as terrible as we think about it, but it, it's-- there are some use cases.

But the, the, the challenge I, I think now, not to say that Copilot is, is not the, the, the great tool, it's just like what you see in those tools is way more in terms of [01:40:00] reasoning and planning compared to, to Copilot

**Speaker 12:** Well, it's that McDerks at eight o'clock to watch the game 

**Speaker:** All right. Well, I hope you enjoyed the first lecture. And then, uh, I'll see you guys hopefully next week. We'll share the slides, we'll share the video for those who, uh, did not have chance to attend. I look forward for next week. 

**Speaker 3:** Thank you. That's 

**Speaker 2:** great.

**Speaker:** Thank you. Thank you. Thank you 

**Speaker 2:** so much. All right. Thank you. Thank you. Bye. 

