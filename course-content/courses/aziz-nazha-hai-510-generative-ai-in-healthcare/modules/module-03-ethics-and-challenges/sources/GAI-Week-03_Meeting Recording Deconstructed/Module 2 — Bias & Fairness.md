# Module 2 — Bias & Fairness

**Speaker 2:** [00:00:00] Bias and fairness, this is another, uh, important, uh, uh, aspect here. And, um, obviously This is, uh, interesting in, in, in part of, again, what we talked about predictive versus generative. In a predictive where the model's predicting a,

a, a treatment or predicting response to treatment, and that response is biased based on the data. So we know that if the data doesn't have all representation of the population that we're treating and we, uh, build an algorithm that could show the outcome or the output may, um, give disadvantage to the, um, uh, underrepresented population.

So we have to be very, very careful with these models in terms of bias, especially the ones even on generative AI side that we start talking now about having the system learn from, from me using it and getting better. But from me [00:01:00] using it, if I'm using it in a biased way, now what I'm doing, I'm making the system more, more biased.

So there are different types, obviously, of, of bias and, and again, this is like a big, big topic we can spend hours talking about. when it comes to, to generative AI it's slightly different than predictive. Just to give you an example, a, a model predicting response, uh, to a population or underrepresented population, um, or preventing them from getting a treatment because they were a minority in, in that training data.

Where in generative AI, it's like generating output that is biased. so we talked about some of those examples. If you go today, I mean that bias still exists. If you go and you say, uh, "Give me an image of a, a CEO of Fortune five hundred company," one hundred percent of time or ninety-nine point nine percent of time you're gonna get an old white male.

if you're gonna say, uh, "Generate an image for, [00:02:00] uh, a nurse," the majority of the time you're gonna get a female. So, so we have that gender bias. It still exists in these models. Part of it is also the training of that data and part of it how is the algorithm is selecting, uh, this. Racial and ethnic bias, um, it's, it's the same thing.

We have the underrepresented minorities in, in the population and then the algorithm, uh, disadvantage them, uh, by, uh, uh, preventing them from getting access to treatment or again generating a content that is irrelevant to that minority of, uh, populations. we have language bias. So, uh, so if you think about ChatGPT and all of these models, training ninety-five percent of the data is in English.

Now, what happened-- uh, and also mainly in the Western countries. So the outcome or the output of these models are really deviated To those countries. So an output [00:03:00] of ChatGPT could be very okay for somebody in the United State. It might be offensive for somebo- somebody in different part of the country, uh, uh, part of the world.

So, so that's the, the geographic, uh, uh, uh, problem. Also, you might have disadvantage for populations that don't have digital, uh, footprint in other languages like what we have in English, and we, we, we... There are many examples, uh, of that in terms of like general bias of the output or whatever the output means for, for us in America, United State or the Western, uh, countries compared to other, uh, small countries that don't have this digital footprint that train the AI So, so, uh, fairness is slightly different than this.

Sometimes it's like, uh, you know, it's like a chicken and egg with these bias and fairness. So fairness is, is the system fair [00:04:00] basically to, to, um, to, uh, minority, uh, or, or, or, or underrepresented populations? Are we preventing specific treatment, or we're over-treating them or under-treating them just because they're not represented enough in the population?

A good example actually got a lot of attention that's on the machine learning side. When you build an algorithm, for example, to detect, uh, uh, cancer in a skin, there was, uh, publications in Nature, uh, in 2017 that's looking at that. and then the idea was like we can build a system where I can take a picture, and the picture will tell me this is skin cancer or not, which improved the dermatology, uh, dermatologist, uh, uh, um, or, or let's say primary care accuracy of diagnosing, uh, melanomas early because it's really hard to get to dermatologists.

Well, it turned out that most of the data that the algorithm is trained on was white skin. So when the algorithm was applied [00:05:00] to, to, uh, uh, uh, people of darker skin or Black skin, the performance of that algorithm dramatically decreased. That's a big, big problem because then, uh, we're not giving the same information for this underrepresented, uh, population.

So, so we have to be careful, very careful or extra careful in healthcare addressing, uh, fairness and, and, and bias of these algorithms and more importantly, continue to monitor them when we deploy them to make sure they don't drift or they get worse over time, and we've seen that. Some models get what they call a drift, which meaning that the model performance get worse over time, and we wanna make sure that it's not getting worse also for underrepresented populations.



