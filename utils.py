#!pip install python-dotenv


import os
from dotenv import load_dotenv, find_dotenv

import numpy as np
from trulens_eval import (
    Feedback,
    TruLlama,
)

import litellm
import trulens_eval
import numpy as np
from trulens_eval import Feedback
from trulens_eval import TruLlama, Tru
from trulens_eval import feedback
from trulens.apps.llamaindex import TruLlama
from trulens_eval.feedback.provider import litellm
from trulens.feedback.v2.feedback import Groundedness
import nest_asyncio

nest_asyncio.apply()

def get_gemini_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("GEMINI_API_KEY")


def get_hf_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("HUGGINGFACE_API_KEY")

get_gemini_api_key()
nest_asyncio.apply()

#GOOGLE_API_KEY=""  # add your GOOGLE API key here
#GEMINI_API_KEY=""  # add your GEMINI API key here
#os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
#os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Initialize provider class
from trulens_eval.feedback.provider.litellm import LiteLLM

litellm = LiteLLM(model_engine="gemini-pro")


# # Initialize groundedness class
grounded = Groundedness(groundedness_provider=litellm)

qa_relevance = (
    Feedback(litellm.relevance_with_cot_reasons, name="Answer Relevance")
    .on_input_output()
)

qs_relevance = (
    Feedback(litellm.relevance_with_cot_reasons, name = "Context Relevance")
    .on_input()
    .on(TruLlama.select_source_nodes().node.text)
    .aggregate(np.mean)
)

f_groundedness = (
    Feedback(litellm.groundedness_measure_with_cot_reasons, name="Groundedness")
        .on(TruLlama.select_source_nodes().node.text)
        .on_output()
)

feedbacks = [qa_relevance, qs_relevance, f_groundedness]

def get_trulens_recorder(query_engine, feedbacks, app_id):
    tru_recorder = TruLlama(
        query_engine,
        app_id=app_id,
        feedbacks=feedbacks
    )
    return tru_recorder

def get_prebuilt_trulens_recorder(query_engine, app_id):
    tru_recorder = TruLlama(
        query_engine,
        app_id=app_id,
        feedbacks=feedbacks
        )
    return tru_recorder

# from llama_index import ServiceContext, VectorStoreIndex, StorageContext
# from llama_index.node_parser import SentenceWindowNodeParser
# from llama_index.indices.postprocessor import MetadataReplacementPostProcessor
# from llama_index.indices.postprocessor import SentenceTransformerRerank
# from llama_index import load_index_from_storage
# import os


# def build_sentence_window_index(
#     document, llm, embed_model="local:BAAI/bge-small-en-v1.5", save_dir="sentence_index"
# ):
#     # create the sentence window node parser w/ default settings
#     node_parser = SentenceWindowNodeParser.from_defaults(
#         window_size=3,
#         window_metadata_key="window",
#         original_text_metadata_key="original_text",
#     )
#     sentence_context = ServiceContext.from_defaults(
#         llm=llm,
#         embed_model=embed_model,
#         node_parser=node_parser,
#     )
#     if not os.path.exists(save_dir):
#         sentence_index = VectorStoreIndex.from_documents(
#             [document], service_context=sentence_context
#         )
#         sentence_index.storage_context.persist(persist_dir=save_dir)
#     else:
#         sentence_index = load_index_from_storage(
#             StorageContext.from_defaults(persist_dir=save_dir),
#             service_context=sentence_context,
#         )

#     return sentence_index


# def get_sentence_window_query_engine(
#     sentence_index,
#     similarity_top_k=6,
#     rerank_top_n=2,
# ):
#     # define postprocessors
#     postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
#     rerank = SentenceTransformerRerank(
#         top_n=rerank_top_n, model="BAAI/bge-reranker-base"
#     )

#     sentence_window_engine = sentence_index.as_query_engine(
#         similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
#     )
#     return sentence_window_engine


# from llama_index.node_parser import HierarchicalNodeParser

# from llama_index.node_parser import get_leaf_nodes
# from llama_index import StorageContext
# from llama_index.retrievers import AutoMergingRetriever
# from llama_index.indices.postprocessor import SentenceTransformerRerank
# from llama_index.query_engine import RetrieverQueryEngine


# def build_automerging_index(
#     documents,
#     llm,
#     embed_model="local:BAAI/bge-small-en-v1.5",
#     save_dir="merging_index",
#     chunk_sizes=None,
# ):
#     chunk_sizes = chunk_sizes or [2048, 512, 128]
#     node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
#     nodes = node_parser.get_nodes_from_documents(documents)
#     leaf_nodes = get_leaf_nodes(nodes)
#     merging_context = ServiceContext.from_defaults(
#         llm=llm,
#         embed_model=embed_model,
#     )
#     storage_context = StorageContext.from_defaults()
#     storage_context.docstore.add_documents(nodes)

#     if not os.path.exists(save_dir):
#         automerging_index = VectorStoreIndex(
#             leaf_nodes, storage_context=storage_context, service_context=merging_context
#         )
#         automerging_index.storage_context.persist(persist_dir=save_dir)
#     else:
#         automerging_index = load_index_from_storage(
#             StorageContext.from_defaults(persist_dir=save_dir),
#             service_context=merging_context,
#         )
#     return automerging_index


# def get_automerging_query_engine(
#     automerging_index,
#     similarity_top_k=12,
#     rerank_top_n=2,
# ):
#     base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
#     retriever = AutoMergingRetriever(
#         base_retriever, automerging_index.storage_context, verbose=True
#     )
#     rerank = SentenceTransformerRerank(
#         top_n=rerank_top_n, model="BAAI/bge-reranker-base"
#     )
#     auto_merging_engine = RetrieverQueryEngine.from_args(
#         retriever, node_postprocessors=[rerank]
#     )
#     return auto_merging_engine

