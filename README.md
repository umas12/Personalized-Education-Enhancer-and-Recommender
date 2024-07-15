# Welcome to P.E.E.R. - Your Personalized Learning Companion!
<p align="center">

<img width="100" alt="PEER" src="https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/assets/58556705/0f0dcb43-6f74-4f84-9176-17c6836a8a37">

</p>

**Authors:**

- Uma Sivakumar, MS in Data Science’24, Texas A&M University.
- Rithvik Srinivasaiya, MS in Data Science'24, Texas A&M University.
- Sriram Balasubramanian, MS in Data Science'24, Texas A&M University.

**Advisor:** Prof. James Caverlee, Department of Computer Science & Engineering, Texas A&M University.
   

Ever felt lost in the sea of educational resources available online? You’re not alone! In today’s digital age, while there's no shortage of information, finding the right learning materials that fit your needs and skill level can be like finding a needle in a haystack. That's why we created **P.E.E.R. (Personalized Education Enhancer and Recommender)** — a one-stop platform that simplifies your search and learning process. P.E.E.R. is a centralized platform that simplifies your learning process by providing educational resources from various popular platforms like Google Books and Udemy, all under one roof. Whether you're starting fresh on a topic or diving deeper into specialized subjects, P.E.E.R. tailors the learning experience to your needs. This means you can spend more time actually learning and less time searching, making your study time both efficient and enjoyable.




## Why P.E.E.R. Could Be Your New Best Study Buddy

- **Saves Time**: No more endless searching. We bring the best of the web in learning materials to you.
- **Learns With You**: As you use the platform, it learns and adapts, getting better at recommending the right materials for you.
- **Supports Your Growth**: With resources tailored to match your current level, you can steadily progress in your studies.


## Where did we collect the data?

We gathered our data from two main sources to offer a broad range of educational content. By using APIs from Google Books and Udemy, we collected about 120k rows of data from Google Books and 40k rows of data from Udemy courses, providing users with diverse resources to explore. To store this data effectively, we turned to Amazon AWS's cloud database. This PostgreSQL database allowed us to organize the data into relational tables, making it easy to access and manage. Before integrating the data into our model, we took the necessary steps to clean and prepare it. This ensured that the data was in optimal condition for use in our model. Our process involved collecting data from multiple sources, storing it in a cloud database, and preprocessing it to maintain its quality. This data was then integrated into our model to generate personalized educational recommendations based on user preferences and interaction history.

## How Does P.E.E.R actually Work?

P.E.E.R has two main functionalities:

1) **Full-Text Search:** P.E.E.R. aggregates educational content from multiple sources, including books and video courses, and presents it in a single, easy-to-access platform. Users can search for a topic and find relevant resources from integrated platforms.
   
2) **Personalized Recommendations Based on User Preferences:** P.E.E.R. analyzes user interactions, preferences, and past searches to deliver personalized recommendations. This helps users discover content that aligns with their interests and learning goals.

**Our Search Engine**

1) We utilize PostgreSQL's Full-Text Search (FTS) capabilities as the main feature for building our search engine.
   
2) FTS processes text data by breaking it into words or tokens, lowercasing, stemming, and removing stopwords, and then converts it into a vector of lexemes stored in a tsvector data type.
   
3) It uses GIN (Generalized Inverted Index) indexing methods to speed up text searching operations, making document retrieval based on search queries much faster compared to using traditional SQL LIKE or regular expressions.
   
4) FTS offers functions to rank results based on their relevance to the search query, considering factors like term frequency, proximity, and significance in the document using weights.
   
5) It supports complex querying capabilities including boolean operators and phrase search, enabling sophisticated search queries that accurately reflect user intent.

**Our Recommendation System**

1) It uses the BERT for natural language processing task and the tokenizer to convert text into a format that BERT can process.
   
2) Book/Online Course descriptions are analyzed and compared using BERT to generate embeddings, which are representations of the text.
   
3) Generated embeddings are cached to avoid redundant computations and can be loaded when recommending resources.
   
4) User interactions, such as clicks on books, are tracked for implicit feedback and stored in the user database.
   
5) Cosine similarity is computed between user-clicked book embeddings and all book embeddings in the database.
    
6) Top books are recommended based on the highest cosine similarity scores, ensuring diverse and relevant recommendations.

**Our User Interface**

The user interface for P.E.E.R was created using Flask and Python. Flask is a lightweight web framework for Python, making it suitable for building simple and efficient web applications.

<p align="center">
  <img width="400" src="https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/assets/58556705/7bab21c3-ece0-4c9b-a361-f9cc3e4cf700" alt="page 1">

  <img width="400" src="https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/assets/58556705/2814614e-041a-4972-abd8-f6a972904432" alt="page 2">
</p>
<p align="center">
  <img width="400" src="https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/assets/58556705/889e7d3d-b9a2-40c9-919a-07d0f57916d9" alt="page 3">

  <img width="400" src="https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/assets/58556705/263c1a96-164b-493f-afed-1e9fc1c7f5cd" alt="page 4">
</p>


**Is P.E.E.R doing good?**

As we strive to improve P.E.E.R.'s performance, user feedback will play a crucial role in evaluating our system. By listening to our users, we can better understand what works well and what can be improved. This feedback loop will help us refine our algorithms and ensure that P.E.E.R. continues to deliver high-quality recommendations.

## Looking Ahead
Creating P.E.E.R. wasn’t a walk in the park. We faced our fair share of challenges, like figuring out which and how many platforms to draw resources from and dealing with massive amounts of data which at times felt like it might blow up our PCs! But through determination and a bit of tech wizardry, we’ve built a system that’s not only robust but also gets smarter over time.

As we look to the future, we’re excited to expand our resource pool, further refine our algorithms, and introduce community features to make learning not just a personal journey but a shared experience.

We plan on integrating more online platforms such as Coursera, LinkedIn Learning, and others. This expansion will provide our users with a broader range of educational resources to explore, enhancing their learning experience and allowing them to discover new and exciting topics. We're also planning to introduce more advanced algorithms, surpassing even BERT in complexity, like XLNet or GNN. These new algorithms will take our recommendation system to the next level, providing even more precise and personalized suggestions for our users.

To support these enhancements, we also plan to implement more robust data-storing systems. These systems will allow for faster computation and retrieval of data, ensuring that users can access the information they need quickly and efficiently.

So, why wait? Dive into P.E.E.R. today and experience a tailored learning journey that respects your pace and preferences, making education not just effective but enjoyable too!

## Materials

[Project Repository](https://github.com/RITHVIK23/Personalized-Education-Enhancer-and-Recommender/tree/main)

[2-min Video](https://www.youtube.com/watch?v=hq2p_ULwxLk)



