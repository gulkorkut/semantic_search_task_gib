

### **Semantic Search Project Report**

* A semantic search project was developed to enable semantic searching of tax rulings, allowing users to quickly and accurately access the information they need. The process involved collecting ruling contents via web scraping, processing them, creating embeddings, and performing semantic search using cosine similarity.

---

### **Technologies and Tools**

* **Libraries and Technologies:**

  * **Web Scraping:** Selenium
  * **Embedding and Semantic Search:**

    * SentenceTransformers (`all-MiniLM-L6-v2`)
    * FAISS (Facebook AI Similarity Search)
    * Cosine Similarity
  * **Database:** MongoDB
  * **Interface:** Streamlit
* **Other Tools:** ChromeDriver, dotenv

---

### **Project Workflow**

#### **Data Collection via Web Scraping**

* **Script:** `link_collection.py`

  * Collected page links from the Revenue Administration’s tax ruling pages using Selenium by waiting for dynamic content to load.
  * Saved all ruling links to `ozelge_links.txt`.
  * A total of 2,200 ruling links were collected from 220 pages.

---

#### **Extracting Ruling Content and Storing in Database**

* **Script:** `icerik_cekme.py`

  * Extracted ruling content, date, subject, and download links using XPath, provided from `variables.py`.
  * Stored extracted data in MongoDB with the following structure:

    ```json
    {
      "id": "Ruling ID",
      "konu": "Subject",
      "ozelge_linki": "Link",
      "ozelge_tarihi": "Date",
      "indirme_linki": "Download Link",
      "icerik": "Text"
    }
    ```
  * All rulings were saved in the database. If a ruling already existed, it was not saved again. Uniqueness was ensured using indexing on `id`.

---

#### **Embedding Creation**

* **Script:** `embedding_olustur.py`

  * Converted ruling texts and subjects into embeddings using SentenceTransformers (`all-MiniLM-L6-v2`).
  * Added embedding fields to MongoDB documents. Updated structure:

    ```json
    {
      "id": "Ruling ID",
      "konu": "Subject",
      "ozelge_linki": "Link",
      "ozelge_tarihi": "Date",
      "indirme_linki": "Download Link",
      "icerik": "Text",
      "embedding": "Embedding (for content)",
      "embedding_konu": "Embedding (for subject)"
    }
    ```
  * Both content and subject embeddings were created and saved in MongoDB.

---

#### **Semantic and Hybrid Search**

* **Scripts:**

  * `cosine_icerik_search.py` (content-based search)
  * `cosine_konu_search.py` (subject-based search)
  * `hibrit_search.py` (combined content and subject search)

#### **Script Functions**

1. **`cosine_icerik_search.py`:**

   * Performs semantic search over ruling **contents** based on user queries.
   * Generates query embedding and calculates **cosine similarity** with content embeddings from MongoDB to return the most relevant results.
   * For faster results, embeddings and other relevant data are saved in a file (e.g., `embedding_icerik_cache.npy`). If the file does not exist, the data is loaded from the database and the file is created. GPU can also be used to speed up queries.

2. **`cosine_konu_search.py`:**

   * Searches ruling **subjects** based on user queries.
   * Generates query embedding and calculates similarity with subject embeddings.

3. **`hibrit_search.py`:**

   * Searches using **both content and subject** embeddings.
   * Combines content and subject similarity scores.
   * Each score is weighted according to the user query.
   * You can try this approach here: [https://semanticsearchgib.streamlit.app/](https://semanticsearchgib.streamlit.app/)

---

#### **Methodology**

* User input text is converted into an embedding using the SentenceTransformers (SBERT) model.
* SBERT extracts the semantic representation (vector) of the query, preserving its meaning.

**Cosine Similarity Calculation:**

* Cosine similarity is calculated between the query embedding and each embedding in the database.
* Cosine similarity provides a similarity score based on the angle between two vectors.

**FAISS Model:**

* Similarity can also be calculated using FAISS with content embeddings.

**Hybrid Model:**

* Cosine similarity scores from content and subject embeddings are combined to produce a total similarity score.
* Results are displayed in the user interface ranked by this total score.

---

### **Streamlit Application**

* To run the Streamlit app:

  ```
    python -m streamlit run streamlit_app.py
  ```
* To install required packages using `requirements.txt`:

  ```
    pip install -r requirements.txt
  ```
