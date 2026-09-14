# 04 - Machine Learning Types

[00:00:00] 


## How Machine Learning Works

**Speaker:** But that's where generative AI started becoming big in the media and then generative AI, uh, evolved to agentic AI, um, and, and then multi-agent systems and, and those things. So, so what is machine learning and how does it work? Um, so machine learning is when you have-- sort of one of the easiest way to think about it is, is that you have an input.

That input could be an image, could be a structured data, could be a video. You have an output, is something you're trying to predict. So in between, you have an algorithm. This algorithm could be machine learning algorithm or a deep learning algorithm. A deep learning algorithm is the idea here that you have the input layers and the output sort of mimicking the neurons [00:01:00] in the brain.

So if you look at the neurons in our brain, we have a neuron body, and those neurons are connected to each other. So when they fire up, we, we, we talk, we, we do all the tasks. If we try to mathematically represent this, this become a neural network. And deep, meaning it has multiple layers, could be a thousand layers, and that's representation of the input layer and then the output layer.

And then the prediction could be a classification problem. So we're talking about, you know, malignant lesion, non-malignant lesion, dog, cat, multi-class: dog, cat, giraffe. Or regression problem. Regression problem is a continuous number, so we're trying to build, uh, uh, uh, like a, a length of stay model. How much the patient will stay in the hospital, that's gonna be a continuous number.

Uh, house prices in Philadelphia, that's a continuous number. So there are different types of machine learning [00:02:00] And, and th-they, uh, differ in their applications and applications in healthcare. And, and, and this is what, what, what I wanna focus on because if you take machine learning and deep learning before...

If we're giving this lecture in two thousand eighteen or nineteen when I-- which, uh, what I was doing at that time, I was talking about machine learning, supervised learning, unsupervised learning, and those stuff. I wasn't talking about generative AI. So, so this is where I wanna distinguish, and I hate to say it's the old, it's not the old AI, but you know, it's evolved to generative AI.

But when we focus on machine learning and deep learning, 


## Supervised Learning

**Speaker:** you have supervised learning, where you, uh, sort of have a label for the data, and then you train the algorithm on that label. Unsupervised learning, you don't have labels, you don't have the data as a scatter, and then you s-asking the algorithm to structure it.

Semi-supervised learning, which is half of the data or maybe subset of the data is labeled and some of it is not, and then the algorithm try to label [00:03:00] that data. And then reinforcement learning is trial and error, and I'll explain in the next few slides. So supervised learning, as we discussed, is, is

**Speaker 3:** Just, just curious on labeled data, meaning it has, you know, some additional information with it? 

**Speaker:** Yeah, that's what I'm explaining in this slide. 

**Speaker 3:** Okay. Sorry. 

**Speaker:** Yeah. No, no problem. Yeah, please keep it interactive. So labeled data mean that you have description of the label. So I have a dataset, dogs and cats. So what I will tell the algorithm, so you would have sort of a table.

This image is a dog, and the label is a dog. This image is a dog, and the label is a dog. That's what labeled data. This is a cat, that's the label. So I take the image and I label it dog, cat, giraffe, and, and, and so forth. In healthcare, I will introduce to the, to the algorithm this is, uh, [00:04:00] um, for example, an image.

This is a bleed, no bleed. So I will give the algorithm a CT scan, and I will label it. So on this CT scan, this is a bleed. On this CT scan, no bleed. Chest X-ray, for example, right? Pneumonia, atelectasis. So that will be the labels of the data. Could be b-binary, so again, bleed, no bleed, or multi-labeled. So on chest X-ray will be atelectasis, pneumonia, uh, normal, uh, uh, pneumothorax, uh, uh congestive heart failure, cardiomegaly, and then I will label all of those.

So that's what means labeled data. And then what I ask the algorithm is to find pattern in the data, and then it spit up and say, "Okay, this is a bleed. This is no bleed." That's what the model will tell me. So if I train the data on dog or a cat and I give it a giraffe, it's gonna guess it as a dog or a [00:05:00] cat, unless I have a label which ca-called others, and then it's gonna put it in others.

So this is part of also labeling. Uh, uh, so it's gonna be dependent on the label. And the way it works, it give you probability, and then you th-- set a threshold to say, you know, above maybe fifty or above sixty, this will be a dog or will be a cat. So the idea here, again, you have the label and then the prediction, and then in between you have a machine learning algorithm or a deep learning algorithm.


## Unsupervised Learning

**Speaker:** Unsupervised learning, you don't have labels. You just have data. So for example, in healthcare, RNA-Seq genomic data where you're not tied to a patient and you, you sort of trying to Find the impact of that data on an outcome. So let's say response to chemotherapy, but you don't know which gene have that impact because you don't [00:06:00] have the label.

So, so what you're asking the algorithm, go find patterns between those genes and based on those patterns, tell me whether the patient gonna respond or not. So this is where it start, what we'll call it clustering. So we say, you know what? It looks like all of these genes or, or could be images or could be anything clustered together and, and then this patient in this cluster will have this outcome, and these patients in this cluster will have different outcome.

So in this example obviously there is no label, uh, in, in, in, in that. The common one obviously in, in healthcare is the clustering which we do a lot in, in genomic and, uh, multi-omic data. 


## Semi-Supervised Learning

**Speaker:** Now, there is something called semi-supervised 'cause you would imagine one of the challenges used to be is labeling the data, right?

Especially in healthcare, because deep learning require a lot of data, [00:07:00] and, um, this is why back in the days it was like, "Oh yeah, artificial intelligence is not, not intelligent," because, you know, I have to label all that data. So, so if I wanna build a model to, to say bleed, no bleed on the brain, I wanna take thousands of images and label them.

It's not gonna be fifty image. I mean, I know we did a lot of research with fifty image. That's not a good model. But imagine sitting and labeling, for example, ten thousand chest X-ray to say, "Oh, this is pneumonia. This is atelectasis." It, it's a lot of labor intensive, uh, work. So one technique was semi-supervised, where you have some of the data is labeled and some of it doesn't have that label, and then you're asking the algorithm, sort of train it on the labeled data and then use the algorithm to predict the label of the, uh, of the unlabeled [00:08:00] data and then, uh, try to build a model and expedite that.

Because again, if I wanna come and say, well, I need about two hundred thousand scans to build a reliable model, that's gonna be a lot of time, effort to label that data 


## Reinforcement Learning

**Speaker:** Reinforcement learning, this is-- used to be, although now we're using it more in a different way, mainly for robotics. And then the idea here, even they used to call them agent, uh, which is different than the agent we're gonna talk about in the next few slide.

But you sort of through, through action, reward, you're trying to, uh, teach the algorithm what to do. Uh, and so, um, you put the algorithm in an environment, and you give it an action. For example, go-- for a robot, go grab this, and if it does it in a certain way, you give it a reward. If it does it in a, [00:09:00] in a, in a wrong way, you, you give it a punishment.

And then the algorithm on its own start based on reward and action, improve itself. So for example, uh, one of this, we're gonna talk about reinforcement learning with the human feedback. When they kind of train, uh, the large language models, they took the output of those large la-language models, have a human review it, and then they taught the system back to say, "You know what?

This is harmful. If somebody asks this question, you shouldn't answer it." So this is how they use reinforcement learning. We use it more, uh, now it used in gaming to imp-- uh, to optimize the algorithm, uh, when they play in game to actually maximize the reward. So that's a different type of things. And again, it, it's mainly in, in also in other way in robotics All right.

So- 

**Speaker 5:** Aziz. Sorry, we have a hand [00:10:00] up from, um- 

**Speaker 6:** Niyasha. 

**Speaker 5:** I think... Yes. Thank you. 

**Speaker 6:** Sure. Um, I was going to go back to the super... the semi-supervised learning, um, and I was hoping you could just explain a little bit more about, like, quality control assurance if, um, the model is only learning off of a small subset, um, and is then predicting, um, using the large unlabeled set.

What, what are the inputs, I guess, like, that are involved to make sure that, like, it's actually learning correctly? 

**Speaker:** Yeah. So, so based on once the model, uh, produce the output, you study the output, and you have a different matrix in studying the output, right? So it's gonna be accuracy, precision, recall, uh, area under the curve, all of those, uh, false positive, uh, negative predictive value, all of those things.

So [00:11:00] in other words, again, if you think about it like, uh, an image and, uh, let's say a CT scan, bleed, no bleed. So s- uh, so you're gonna focus on the unlabeled one. So the way you do it, you split the data into training and test. You take the test data, and then you apply the final model on it. And then in that time, you're just saying bleed, no bleed, and then you're gonna go and, and score the, the system on, on that.

Obviously, for the validation, you need the labeled data 'cause you wanna make sure that the model is valid. 

**Speaker 6:** I guess I'm just curious as to, like, how this represents less work than the supervised learning. It seems like the work has just been shifted to, like, validation instead of labeling. 

**Speaker:** No, because then you're using the labeled and the algorithm to sort of label the rest of the data, if that makes sense.

So instead of having all the data labeled, [00:12:00] you're using the label in some of that subset to label the large data through that process, if it makes sense too. So you don't need all of, all of this data to be labeled. Now, that doesn't mean you might get a better model. You might not get a better model compared to fully labeled data.

But it's a way to get maybe, if you're unable to label the entire data set, to get you somewhere. But I can tell you from my experience, this is not where... it's not gonna be comparable to a full data set that has the full labels. But it's another way to get you closer there, if that makes sense. 

**Speaker 2:** Yeah. Thank you.

**Speaker:** Uh, okay. So another hand

**Speaker 7:** Uh, yeah. So I, I think I just had a follow-up to what we were discussing because it came to my mind as well. Um, how much human effort is then actually re-needed to assess reliability? You are labeling an unlabeled [00:13:00] data set. There is a lot of, of... I, I... If you put a statistician in our room, they were like, "I'm not gonna trust AI to label the data set."

Yeah. Because there is a lot of human effort spent on, on doing this. So how do we rely on that? 

**Speaker:** It used to be. So remember here we're living in the two thousands, and you're right. So what a lot of companies start doing, start hiring a human labeler. So for example, there is a big project done at Google where they took the, uh, in the, uh, uh, the, um, fundus of the eye to try to identify diabetic retinopathy, and they labeled a hundred fifty thousand labels.

So they used a human to do that. So in the past, we used a lot of human to label the data. Now with generative AI, it's way much better You need to have some quality checks too, and we will get to that too, but it become much [00:14:00] easier. This is why in the past you see some of the research where, oh, we did, uh, um, build a model to predict response on a CT scan, and we use fifty CT scan to do this and fifty CT...

These are not reliable models. But, but for, for those radiology things, yeah, they use a lot of human labeling at the beginning. The same thing where segmentation, for example, like, uh, they train the model to, to segment, for example, the heart and those things. Now, algorithms evolved, so for segmentation, meaning the, the, the algorithm can identify, for example, the heart on the chest X-ray, identify the lung.

The algorithm, uh, improvement also enabled us to make the segmentation much faster and better, uh, and then but still a human needs to verify it. This is why it took a lot of time and effort to do that. With [00:15:00] generative AI, what you will see, it's much better now. Um, so what you're also alluding to is something we will learn in module three, which is called trust, trust of AI system, and that's part of the ethical and challenges that we're gonna learn.

Uh, trust takes time and, uh, need to be earned. So, so we'll talk more about that in, in module three

All right. Uh, I guess this is just examples of, of what, what is, what is, uh, uh... Keep in mind, this is sort of categorical, right? So for example, pneumonia, no pneumonia, that's a binary outcome, uh, prediction. Where how many days this patient gonna stay in ICU, that's a regression problem. So that's the whole purpose of this.

