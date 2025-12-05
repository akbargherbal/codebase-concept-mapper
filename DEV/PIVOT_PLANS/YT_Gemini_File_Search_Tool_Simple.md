```python
%pip install -q -U "google-genai>=1.43.0"
```

    [?25l     [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m0.0/46.7 kB[0m [31m?[0m eta [36m-:--:--[0m[2K     [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m46.7/46.7 kB[0m [31m3.3 MB/s[0m eta [36m0:00:00[0m
    [?25h[?25l   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m0.0/256.1 kB[0m [31m?[0m eta [36m-:--:--[0m[2K   [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m256.1/256.1 kB[0m [31m14.1 MB/s[0m eta [36m0:00:00[0m
    [?25h

## Gemini File Search Tool API: Getting started with file grounding for Gemini models

<a target="_blank" href="https://colab.research.google.com/drive/1qOH73lDHMEUk_J0Zo_rwk_6tW0L1Ix1I?usp=sharing"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>


```python
import os
from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')
```


```python
# !wget https://arxiv.org/pdf/1706.03762.pdf -O document.pdf

!wget https://storage.courtlistener.com/recap/gov.uscourts.cand.433688/gov.uscourts.cand.433688.340.1.pdf -O document.pdf
```

    --2025-11-09 05:45:19--  https://storage.courtlistener.com/recap/gov.uscourts.cand.433688/gov.uscourts.cand.433688.340.1.pdf
    Resolving storage.courtlistener.com (storage.courtlistener.com)... 18.65.39.29, 18.65.39.128, 18.65.39.110, ...
    Connecting to storage.courtlistener.com (storage.courtlistener.com)|18.65.39.29|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 229009 (224K) [application/pdf]
    Saving to: ‘document.pdf’
    
    document.pdf          0%[                    ]       0  --.-KB/s               document.pdf        100%[===================>] 223.64K  --.-KB/s    in 0.01s   
    
    2025-11-09 05:45:19 (22.2 MB/s) - ‘document.pdf’ saved [229009/229009]
    
    


```python
from google import genai
from google.genai import types
import time
```


```python
client = genai.Client()

# Create the file search store with an optional display name
file_search_store = client.file_search_stores.create(config={'display_name': 'sam-basic'})
```


```python
file_search_store
```




    FileSearchStore(
      create_time=datetime.datetime(2025, 11, 9, 5, 46, 29, 539720, tzinfo=TzInfo(UTC)),
      display_name='sam-basic',
      name='fileSearchStores/sambasic-luhezy3p7ter',
      update_time=datetime.datetime(2025, 11, 9, 5, 46, 29, 539720, tzinfo=TzInfo(UTC))
    )




```python
# Create a file search store (including optional display_name for easier reference)
# file_search_store = client.file_search_stores.create(config={'display_name': 'my-file_search-store-123'})

# List all your file search stores
for file_search_store in client.file_search_stores.list():
    print(file_search_store)
```

    name='fileSearchStores/sambasic-luhezy3p7ter' display_name='sam-basic' create_time=datetime.datetime(2025, 11, 9, 5, 46, 29, 539720, tzinfo=TzInfo(UTC)) update_time=datetime.datetime(2025, 11, 9, 5, 46, 29, 539720, tzinfo=TzInfo(UTC)) active_documents_count=None pending_documents_count=None failed_documents_count=None size_bytes=None
    


```python
# Upload and import a file into the file search store, supply a file name which will be visible in citations
operation = client.file_search_stores.upload_to_file_search_store(
  file='/content/document.pdf',
  file_search_store_name=file_search_store.name,
  config={
      'display_name' : 'Illya Testimony 01',
  }
)
```


```python
client.operations.get(operation)
```




    UploadToFileSearchStoreOperation(
      done=True,
      name='fileSearchStores/sambasic-luhezy3p7ter/upload/operations/illya-testimony-01-e6l53qvklyw5',
      response=UploadToFileSearchStoreResponse(
        document_name='fileSearchStores/sambasic-luhezy3p7ter/documents/illya-testimony-01-e6l53qvklyw5',
        parent='fileSearchStores/sambasic-luhezy3p7ter'
      )
    )




```python
# Wait until import is complete
while not operation.done:
    time.sleep(5)
    print("Waiting")
    operation = client.operations.get(operation)

print("Done")
```

    Done
    


```python
PROMPT = "Tell me about this document"

#  Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""{PROMPT}\n (return your answer in markdown as sections and bullet points)\nANSWER:\n""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

    This document is a highly confidential videotaped deposition transcript of Ilya Sutskever, taken on October 1, 2025, in San Francisco, California. The deposition is part of a legal case titled "MUSK v. ALTMAN" in the United States District Court, Northern District of California, Oakland Division, Case No. 4:24-cv-04722-YGR.
    
    ### Key Aspects of the Document:
    
    *   **Deponent:** Ilya Sutskever.
    *   **Date of Deposition:** Wednesday, October 1, 2025, commencing at 10:19 AM and concluding at 8:07 PM.
    *   **Legal Case:** *Elon Musk, et al. v. Samuel Altman, et al.*
    *   **Confidentiality:** The document is marked as "Highly Confidential."
    
    ### Content Regarding a Prepared Memo (Exhibit 19):
    
    *   **Preparation:** Ilya Sutskever prepared a document referred to as "Exhibit 19" at the request of independent board members, most likely Adam D'Angelo.
    *   **Purpose:** The memo was intended to "paint a picture from a large number of small pieces of evidence or items," utilizing screenshots largely obtained from Mira Murati.
    *   **Allegations against Sam Altman:** The first page of Exhibit 19 states: "Sam exhibits a consistent pattern of lying, undermining his execs, and pitting his execs against one another."
    *   **Sutskever's View:** Sutskever confirmed this statement reflected his view at the time and that he had previously expressed these concerns to the independent directors, including Adam D'Angelo, Helen Toner, and Tasha McCauley.
    *   **Desired Action:** Sutskever believed that termination of Sam Altman was an appropriate action based on his concerns.
    *   **Method of Delivery:** The memo was sent using a "disappearing email" because Sutskever was concerned about the memos leaking.
    *   **Exhibit 19 Handling:** There was an agreement among the parties to keep the marked copy of Exhibit 19, and other copies were to be returned after three days.
    
    ### Discussion Regarding OpenAI's Mission:
    
    *   **Helen Toner's Comment:** Ilya Sutskever recalled Helen Toner telling employees that allowing OpenAI to be destroyed, if Sam Altman did not return, would be consistent with the company's mission.
    *   **Sutskever's Reaction:** While he did not recall his exact reaction at the time, Sutskever stated that, at that point, he definitely did not think allowing the company's destruction was consistent with the mission, except under hypothetical extreme circumstances.
    


```python
print(response.candidates[0].grounding_metadata)
```

    google_maps_widget_context_token=None grounding_chunks=[GroundingChunk(
      retrieved_context=GroundingChunkRetrievedContext(
        text="""--- PAGE 1 ---
    
    EXHIBIT 4
    
    
    --- PAGE 2 ---
    
    In the Matter Of:
    
    MUSK v
    
    ALTMAN
    
    ILYA SUTSKEVER
    
    October 01, 2025
    
    LEXITAS™
    
    
    --- PAGE 3 ---
    
    1
    
    2
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    UNITED STATES DISTRICT COURT
    
    NORTHERN OF CALIFORNIA
    
    OAKLAND DIVISION
    
    3
    
    4
    
    ELON MUSK, et al.,
    
    )
    
    5
    
    Plaintiffs,
    
    )
    
    6
    
    V.
    
    )
    
    7
    
    SAMUEL ALTMAN, et al.,
    
    )
    
    )
    
    8
    
    Defendants.
    
    )
    
    9
    
    10
    
    11
    
    12
    
    13
    
    14
    
    15
    
    16
    
    17
    
    18
    
    19
    
    20
    
    21
    
    22
    
    23
    
    24
    
    25
    
    Ilya Sutskever
     October 01, 2025
    
    1
    
    Case No. 4:24-cv-04722-YGR
    
    ** HIGHLY CONFIDENTIAL **
    
    Videotaped Deposition of ILYA SUTSKEVER
    
    San Francisco, California
    
    Wednesday, October 1, 2025
    
    Reported Stenographically by
    
    Michael P. Hensley, RDR, CSR No. 14114
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 1
    
    
    --- PAGE 4 ---
    
    1
    
    2
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    UNITED STATES DISTRICT COURT
    
    NORTHERN OF CALIFORNIA
    
    OAKLAND DIVISION
    
    3
    
    4
    
    ELON MUSK, et al.,
    
    )
    
    5
    
    Plaintiffs,
    
    )
    
    )
    
    6
    
    V.
    
    )
    
    7
    
    SAMUEL ALTMAN, et al.,
    
    )
    
    )
    
    8
    
    Defendants.
    
    )
    
    )
    
    9
    
    10
    
    11
    
    12
    
    13
    
    14
    
    15
    
    16
    
    17
    
    18
    
    19
    
    20
    
    21
    
    22
    
    23
    
    24
    
    25
    
    Ilya Sutskever
     October 01, 2025
    
    2
    
    Case No. 4:24-cv-04722-YGR
    
    Videotaped Deposition of ILYA SUTSKEVER,
    
    commencing at the hour of 10:19 AM and concluding at
     the hour of 8:07 PM on Wednesday, October 1, 2025,
     at the location of Cooley, LLP,
    
    3 Embarcadero Center, 20th Floor, San Francisco,
     California 94111, before Michael Hensley, Registered
     Diplomate Reporter, Certified Shorthand Reporter
    
    No. 14114, in and for the State of California.
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 2
    
    
    --- PAGE 5 ---
    
    MUSK v
    
    
    ,"Highly Confidential
    
    
    ALTMAN
    ","October 01, 2025
    "
    "1
    ","APPEARANCES:
    ","3
    "
    "2
    ","For Plaintiffs:
    ",
    "3
    ","MOLOLAMKEN LLP
    ",
    "4
    ","BY:
    
    
    STEVEN F. MOLO, ESQ.
     JENNIFER SCHUBERT, ESQ.
     SARA TOFIGHBAKHSH, ESQ.
    ",
    "5
    ","430 Park Avenue
    ",
    ,"New York, New York 10022
    ",
    "6
    ",,
    ,"212.607.8170
     smolo@mololamken.com
    ",
    "7
    ","jschubert@mololamken.com
    ",
    ,"stofighbakhsh@mololamken.com
    ",
    "8
    ",,
    "9
    ","For Defendant Microsoft Corporation:
    ",
    "10
    
    
    11
    ","DECHERT LLP
     RUSSELL P. COHEN ESQ.
     BY:
     YOSEF WEITZMAN, ESQ.
    ",
    "12
    
    
    13
    
    
    14
    ","45 Fremont Street, 26th Floor
     San Francisco, California 94105
     415.262.4506
    
    
    russ.cohen@dechert.com
     yosi.weitzman@dechert.com
    ",
    "15
    ","For Defendant OpenAI:
    ",
    "16
    
    
    17
    ","WACHTELL, LIPTON, ROSEN & KATZ
     SARAH K. EDDY, ESQ.
     BY:
     KELSEY""",
        title='Illya Testimony 01'
      )
    ), GroundingChunk(
      retrieved_context=GroundingChunkRetrievedContext(
        text="""WITNESS: So the way I wrote this
    
    13:52:25 25
    
    document was to
    
    the context for this document is
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 128
    
    
    --- PAGE 8 ---
    
    1
    
    2
    
    3
    
    4
    
    13:52:56
    
    5
    
    6
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    that the independent board members asked me to
     prepare it. And I did.
    
    And I was pretty careful. Most of the
     screenshots that I have that I most or all, I
    
    don't remember. I get them from Mira Murati.
    
    Ilya Sutskever
     October 01, 2025
    
    It made sense to include them in order to
    
    129
    
    7
    
    8
    
    paint a picture from a large number of small pieces
     of evidence or items.
    
    9
    
    BY ATTORNEY MOLO:
    
    13:53:14 10
    
    Q.
    
    Okay.
    
    11
    
    And which independent directors asked you
    
    12
    
    to prepare your memo Exhibit 19?
    
    13
    
    A.
    
    It was most likely Adam D'Angelo.
    
    14
    
    Q.
    
    Okay.
    
    13:53:26 15
    
    And did you recall when he asked you to do
    
    16
    
    that?
    
    17
    
    A.
    
    No.
    
    18
    
    Q.
    
    Okay.
    
    19
    
    Do you recall what it was that he said to
    
    13:53:32 20
    
    you that
    
    caused you to prepare this memo?
    
    21
    
    A.
    
    I don't remember what he said exactly.
    
    22
    
    Q.
    
    What's your best recollection of what he
    
    23
    
    said?
    
    24
    
    A.
    
    He said something like
    
    he ask me if I
    
    13:53:43 25
    
    have screenshots.
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 129
    
    
    --- PAGE 9 ---
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    1
    
    Q.
    
    2
    
    3
    
    Well, before he asked you if you had
     screenshots, I mean, what caused him to your
     knowledge, you know, to ask you to prepare this?
    
    A.
    
    I had discussions with the independent
    
    4
    
    13:53:56
    
    5
    
    Ilya Sutskever
     October 01, 2025
    
    130
    
    board members discussing the subject matter of these
     documents. And after""",
        title='Illya Testimony 01'
      )
    ), GroundingChunk(
      retrieved_context=GroundingChunkRetrievedContext(
        text="""this?
    
    A.
    
    I had discussions with the independent
    
    4
    
    13:53:56
    
    5
    
    Ilya Sutskever
     October 01, 2025
    
    130
    
    board members discussing the subject matter of these
     documents. And after having some discussions,
    
    6
    
    7
    
    either Adam or the three of them together, I don't
    
    8
    
    remember, have asked me to collect supporting
    
    9 screenshots.
    
    13:54:11 10
    
    Q.
    
    Okay.
    
    11
    
    And the three of them together were Adam
    
    12
    
    D'Angelo, Helen Toner, and Tasha McCauley?
    
    13
    
    A.
    
    Correct.
    
    14
    
    Q.
    
    All right.
    
    13:54:20 15
    
    And the document that you prepared, the
    
    16 very first page says:
    
    17
    
    18
    
    19
    
    13:54:31 20
    
    21
    
    A.
    
    [As Read] Sam exhibits a consistent
     pattern of lying, undermining his execs,
     and pitting his execs against one another.
     That was clearly your view at the time?
     Correct.
    
    22
    
    Q.
    
    All right.
    
    23
    
    And the you had expressed that view to
    
    24
    
    the independent directors before sending them this
    
    13:54:43 25
    
    memo?
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 130
    
    
    --- PAGE 10 ---
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    Ilya Sutskever
     October 01, 2025
    
    131
    
    1
    
    A.
    
    Correct.
    
    2
    
    Q.
    
    All right.
    
    3
    
    Did they express concern over that to you?
    
    4
    
    A.
    
    Correct.
    
    13:54:48
    
    5
    
    Q.
    
    And did you want them to take action over
    
    6
    
    what you wrote?
    
    7
    
    ATTORNEY AGNOLUCCI: Object to form.
    
    8
    
    THE WITNESS: I wanted them to become
    
    9
    
    aware of it. But my opinion was that action was
    
    13:55:13 10
    
    appropriate.
    
    11
    
    BY ATTORNEY MOLO:
    
    12
    
    Q. Okay.
    
    13
    
    And what action did you think was
    
    14
    
    appropriate?
    
    13:55:25 15
    
    A.
    
    Termination.
    
    16
    
    Q.
    
    Okay.
    
    17
    
    And you sent it using a form of a
    
    18
    
    disappearing email; is that right?
    
    19
    
    A.
    
    Yes.
    
    13:55:34 20
    
    Q.
    
    Why?
    
    21
    
    A.
    
    Because I was worried that those memos
    
    22
    
    will somehow leak.
    
    23
    
    Q.
    
    Okay.
    
    24
    
    What would happen if they leaked?
    
    13:55:44 25
    
    ATTORNEY AGNOLUCCI: Object to form.
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 131
    
    
    ---""",
        title='Illya Testimony 01'
      )
    ), GroundingChunk(
      retrieved_context=GroundingChunkRetrievedContext(
        text="""we reserve all rights, and we note that
    
    12
    
    for the record.
    
    13
    
    ATTORNEY COHEN: And counsel for Microsoft
    
    14
    
    joins that objection.
    
    20:04:49 15
    
    16
    
    ATTORNEY AGNOLUCCI: And can
     clarify your comment about financials.
    
    just to
    
    17
    
    Do you mean financial documents?
    
    18
    
    ATTORNEY MOLO: I don't know what you're
    
    19
    
    talking about.
    
    20:04:57 20
    
    ATTORNEY AGNOLUCCI: You had an objection
    
    21
    
    22
    
    on the basis of documents that weren't produced, and
     you said something about financials.
    
    23
    
    ATTORNEY MOLO: Oh, no. The question's to
    
    24
    
    Ilya about his financial interest in OpenAI.
    
    20:05:15 25
    
    ATTORNEY AGNOLUCCI: Understood. But
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 363
    
    
    --- PAGE 61 ---
    
    MUSK v
    
    ALTMAN
    
    Highly Confidential
    
    Ilya Sutskever
     October 01, 2025
    
    364
    
    1
    
    you're not talking about any documents.
    
    2
    
    ATTORNEY MOLO: I don't know if there are
    
    3
    
    documents that relate to that.
    
    4
    
    ATTORNEY AGNOLUCCI: Well, they they
    
    20:05:22
    
    5
    
    6
    
    weren't within the scope of the subpoena called for
     or the subject of any
    
    7
    
    ATTORNEY MOLO: We'll take it up with the
    
    8
    
    court. That's why there's courts.
    
    9
    
    ATTORNEY AGNOLUCCI: And so last thing,
    
    20:05:29 10
    
    11
    
    12
    
    actually. Exhibit 19. In accordance with the
     parties agreement, we are going to keep the marked
     copy of Exhibit 19.
    
    13
    
    14
    
    20:05:41 15
    
    16
    
    If there are other copies of Exhibit 19,
     the agreement was that, I believe, the parties can
     keep it for three days and then have to return it.
     But we're happy to take the copies now.
    
    17
    
    But, I guess, so that we have a clear
    
    18
    
    record, who has a""",
        title='Illya Testimony 01'
      )
    ), GroundingChunk(
      retrieved_context=GroundingChunkRetrievedContext(
        text="""do you recall Helen
    
    6
    
    7
    
    Toner telling employees that allowing the company to
     be destroyed would be consistent with the mission?
    
    8
    
    A.
    
    I do recall.
    
    9
    
    Q.
    
    And what was the context of that comment?
    
    18:54:12 10
    
    A.
    
    The executives
    
    it was a meeting with
    
    11
    
    the board members and the executive team. The
    
    12
    
    13
    
    14
    
    executives told the board that, if Sam does not
     return, then OpenAI will be destroyed, and that's
     inconsistent with OpenAI's mission.
    
    18:54:29 15
    
    16
    
    And Helen Toner said something to the
     effect of that it is consistent, but I think she
    
    17
    
    said it even more directly than that.
    
    18
    
    Q.
    
    More directly than you've related here?
    
    19
    
    A.
    
    Yes.
    
    18:54:40 20
    
    Q.
    
    Okay.
    
    21
    
    And what was your reaction to that?
    
    22
    
    A.
    
    I don't remember my reaction at the time.
    
    23
    
    Q.
    
    Did you think that would be consistent
    
    24
    
    with the mission?
    
    18:54:54 25
    
    ATTORNEY AGNOLUCCI: Object to form.
    
    www.LexitasLegal.com/Premier
    
    Lexitas
    
    888-267-1200 Page 307
    
    
    --- PAGE 27 ---
    
    MUSK v
     ALTMAN
    
    Highly Confidential
    
    Ilya Sutskever
     October 01, 2025
    
    THE WITNESS: I could imagine hypothetical
    
    308
    
    1
    
    2
    
    extreme circumstances that answer would be "Yes";
    
    3
    
    4
    
    but at that point in time, the answer was definitely
     "No" for me.
    
    18:55:08
    
    5
    
    BY ATTORNEY EDDY:
    
    6
    
    Q. I wanted to just ask a few questions about
    
    7
    
    this document that
    
    8
    
    A.
    
    Yes, please.
    
    9
    
    Q.
    
    you prepared
    
    18:55:15 10
    
    A.
    
    Yes.
    
    11
    
    Q.
    
    Exhibit 19.
    
    12
    
    A.
    
    Yes.
    
    13
    
    Q.
    
    Did did you show the final document
    
    14
    
    that
    
    this document here, Exhibit 19, to Mira
    
    18:55:25 15
    
    Murati?
    
    16
    
    A.
    
    I think it is possible and likely, but I
    
    17
    
    don't have a definite recollection.
    
    18
    
    Q.
    
    Okay.
    
    19
    
    And did you show it to anybody else""",
        title='Illya Testimony 01'
      )
    )] grounding_supports=[GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=146,
        text='This document is a highly confidential videotaped deposition transcript of Ilya Sutskever, taken on October 1, 2025, in San Francisco, California.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=325,
        start_index=307,
        text='4:24-cv-04722-YGR.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=394,
        start_index=361,
        text='*   **Deponent:** Ilya Sutskever.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=500,
        start_index=395,
        text='*   **Date of Deposition:** Wednesday, October 1, 2025, commencing at 10:19 AM and concluding at 8:07 PM.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=565,
        start_index=564,
        text='*'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        0,
      ],
      segment=Segment(
        end_index=639,
        start_index=566,
        text='*   **Confidentiality:** The document is marked as "Highly Confidential."'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        1,
      ],
      segment=Segment(
        end_index=849,
        start_index=694,
        text='*   **Preparation:** Ilya Sutskever prepared a document referred to as "Exhibit 19" at the request of independent board members, most likely Adam D\'Angelo.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        1,
      ],
      segment=Segment(
        end_index=1024,
        start_index=850,
        text='*   **Purpose:** The memo was intended to "paint a picture from a large number of small pieces of evidence or items," utilizing screenshots largely obtained from Mira Murati.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        2,
      ],
      segment=Segment(
        end_index=1213,
        start_index=1025,
        text='*   **Allegations against Sam Altman:** The first page of Exhibit 19 states: "Sam exhibits a consistent pattern of lying, undermining his execs, and pitting his execs against one another."'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        2,
      ],
      segment=Segment(
        end_index=1445,
        start_index=1214,
        text="*   **Sutskever's View:** Sutskever confirmed this statement reflected his view at the time and that he had previously expressed these concerns to the independent directors, including Adam D'Angelo, Helen Toner, and Tasha McCauley."
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        2,
      ],
      segment=Segment(
        end_index=1568,
        start_index=1446,
        text='*   **Desired Action:** Sutskever believed that termination of Sam Altman was an appropriate action based on his concerns.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        2,
      ],
      segment=Segment(
        end_index=1700,
        start_index=1569,
        text='*   **Method of Delivery:** The memo was sent using a "disappearing email" because Sutskever was concerned about the memos leaking.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        3,
      ],
      segment=Segment(
        end_index=1864,
        start_index=1701,
        text='*   **Exhibit 19 Handling:** There was an agreement among the parties to keep the marked copy of Exhibit 19, and other copies were to be returned after three days.'
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        4,
      ],
      segment=Segment(
        end_index=2110,
        start_index=1910,
        text="*   **Helen Toner's Comment:** Ilya Sutskever recalled Helen Toner telling employees that allowing OpenAI to be destroyed, if Sam Altman did not return, would be consistent with the company's mission."
      )
    ), GroundingSupport(
      grounding_chunk_indices=[
        4,
      ],
      segment=Segment(
        end_index=2379,
        start_index=2111,
        text="*   **Sutskever's Reaction:** While he did not recall his exact reaction at the time, Sutskever stated that, at that point, he definitely did not think allowing the company's destruction was consistent with the mission, except under hypothetical extreme circumstances."
      )
    )] retrieval_metadata=None retrieval_queries=None search_entry_point=None source_flagging_uris=None web_search_queries=None
    


```python
for key in response.candidates[0].grounding_metadata.__dict__.keys():
    print(key)
```

    google_maps_widget_context_token
    grounding_chunks
    grounding_supports
    retrieval_metadata
    retrieval_queries
    search_entry_point
    source_flagging_uris
    web_search_queries
    


```python
response.candidates[0].grounding_metadata.grounding_supports[1], response.candidates[0].grounding_metadata.grounding_chunks[1]
```




    (GroundingSupport(
       grounding_chunk_indices=[
         1,
       ],
       segment=Segment(
         end_index=1103,
         start_index=1048,
         text='He believed that termination was the appropriate action'
       )
     ),
     GroundingChunk(
       retrieved_context=GroundingChunkRetrievedContext(
         text="""this?
     
     A.
     
     I had discussions with the independent
     
     4
     
     13:53:56
     
     5
     
     Ilya Sutskever
      October 01, 2025
     
     130
     
     board members discussing the subject matter of these
      documents. And after having some discussions,
     
     6
     
     7
     
     either Adam or the three of them together, I don't
     
     8
     
     remember, have asked me to collect supporting
     
     9 screenshots.
     
     13:54:11 10
     
     Q.
     
     Okay.
     
     11
     
     And the three of them together were Adam
     
     12
     
     D'Angelo, Helen Toner, and Tasha McCauley?
     
     13
     
     A.
     
     Correct.
     
     14
     
     Q.
     
     All right.
     
     13:54:20 15
     
     And the document that you prepared, the
     
     16 very first page says:
     
     17
     
     18
     
     19
     
     13:54:31 20
     
     21
     
     A.
     
     [As Read] Sam exhibits a consistent
      pattern of lying, undermining his execs,
      and pitting his execs against one another.
      That was clearly your view at the time?
      Correct.
     
     22
     
     Q.
     
     All right.
     
     23
     
     And the you had expressed that view to
     
     24
     
     the independent directors before sending them this
     
     13:54:43 25
     
     memo?
     
     www.LexitasLegal.com/Premier
     
     Lexitas
     
     888-267-1200 Page 130
     
     
     --- PAGE 10 ---
     
     MUSK v
      ALTMAN
     
     Highly Confidential
     
     Ilya Sutskever
      October 01, 2025
     
     131
     
     1
     
     A.
     
     Correct.
     
     2
     
     Q.
     
     All right.
     
     3
     
     Did they express concern over that to you?
     
     4
     
     A.
     
     Correct.
     
     13:54:48
     
     5
     
     Q.
     
     And did you want them to take action over
     
     6
     
     what you wrote?
     
     7
     
     ATTORNEY AGNOLUCCI: Object to form.
     
     8
     
     THE WITNESS: I wanted them to become
     
     9
     
     aware of it. But my opinion was that action was
     
     13:55:13 10
     
     appropriate.
     
     11
     
     BY ATTORNEY MOLO:
     
     12
     
     Q. Okay.
     
     13
     
     And what action did you think was
     
     14
     
     appropriate?
     
     13:55:25 15
     
     A.
     
     Termination.
     
     16
     
     Q.
     
     Okay.
     
     17
     
     And you sent it using a form of a
     
     18
     
     disappearing email; is that right?
     
     19
     
     A.
     
     Yes.
     
     13:55:34 20
     
     Q.
     
     Why?
     
     21
     
     A.
     
     Because I was worried that those memos
     
     22
     
     will somehow leak.
     
     23
     
     Q.
     
     Okay.
     
     24
     
     What would happen if they leaked?
     
     13:55:44 25
     
     ATTORNEY AGNOLUCCI: Object to form.
     
     www.LexitasLegal.com/Premier
     
     Lexitas
     
     888-267-1200 Page 131
     
     
     ---""",
         title='Illya Testimony 01'
       )
     ))




```python
PROMPT = "What did Ilya see?"

#  Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""{PROMPT}\n (return your answer in markdown as sections and bullet points)\nANSWER:\n""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
```

### Deleting Your Stores


```python
# deleting the stores
# List all your file search stores
for file_search_store in client.file_search_stores.list():
    name = file_search_store.name
    print(name)
    # Get a specific file search store by name
    my_file_search_store = client.file_search_stores.get(name=file_search_store.name)

    # Delete a file search store
    client.file_search_stores.delete(name=name, config={'force': True})
```

    fileSearchStores/sambasic-luhezy3p7ter
    
