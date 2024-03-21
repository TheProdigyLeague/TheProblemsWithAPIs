# begin hacks and the installing of third-party mods
import os
import sys
import json
import re
import pandas
import numbers
import numpy
import time
import _future_
import random
import logging
import subprocess
import shutil
from functools import lru_cache
from http.server import HTTPServer, SimpleHTTPRequestHandler
from importlib import metadata
from multiprocessing import pool
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Container, DefaultDict, Dict, List, Set, Union, cast, Optional
`
import httpx
import yaml
from github import Github
from pydantic import BaseModel, BaseSettings SecretStr
from pydantic_settings import BaseSettings
`
import mkdocs.commands.build
import mkdocs.commands.serve
import mkdocs.config
import mkdocs.utils
import typer
import yaml
from jinja2 import Template
`
# begin script kiddie bs
logging.basicConfig(level=logging.INFO)
`
app = typer.Typer()
`
mkdocs_name = "mkdocs.yml"
`
missing_translation_snippet = """
{!../../../docs/missing-translation.md!}
"""
`
docs_path = Path("docs")
en_docs_path = Path("docs/en")
en_config_path: Path = en_docs_path / mkdocs_name
site_path = Path("site").absolute()
build_site_path = Path("site_build").absolute()
`
awaiting_label = "awaiting-review"
lang_all_label = "lang-all"
approved_label = "approved-2"
translations_path = Path(__file__).parent / "translations.yml"
`
github_graphql_url = "https://api.github.com/graphql"
questions_category_id = "MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMDAxNDM0"
questions_translations_category_id = "DIC_kwDOCZduT84CT5P9"
`
discussions_query = """ 
  query Q($after: String, $category_id: ID)
    repository(name: "fastapi", owner: "tiangolo")
      { discussions (first: 100, after: $after, categoryID: $category_id) { edges { cursor node { number author { login avatarUrl url } title createdAt comments(first: 100) { nodes { createdAt author { login avatarUrl url } isAnswer replies(first: 10) { nodes { createdAt author { login avatarUrl url }}}}}}}}} """
`
prs_query = """
"query Q($after: String)
{ repository(name: "fastapi", owner: "tiangolo" { pullRequests(first:100, after: $after) { edges { cursor node { number labels(first: 100) { nodes { name }} author { login avatarUrl url } title createdAt state comments(first: 100) { nodes { createdAt author { login avatarUrl url }}} reviews(first:100 { nodes { author { login avatarUrl url } state }}}}}}} """
`
sponsors_query = """
query Q($after: String) { user(login: "tiangolo") { sponsorshipsAsMaintainer(first: 100, after: $after) { edges { cursor { node { sponsorEntity { ... on Organization { login avatarUrl url } ... on User { login avatarUrl url }} tier { name monthlyPriceInDollars }}}}}}"""
`
translation_discussion_query = """
query Q($after: String, $discussion_number: Int!) {
  repository(name: "fastapi", owner: "tiangolo") {
    discussion(number: $discussion_number) {
      comments(first: 100, after: $after) {
        edges {
          cursor
          node {
            id
            url
            body
          }
        }
      }
    }
  }
}
"""
`
all_discussions_query = """
query Q($category_id: ID) {
  repository(name: "fastapi", owner: "tiangolo") {
    discussions(categoryId: $category_id, first: 100) {
      nodes {
        title
        id
        number
        labels(first: 10) {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
  }
}
"""

add_comment_mutation = """
mutation Q($discussion_id: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $discussion_id, body: $body}) {
    comment {
      id
      url
      body
    }
  }
}
"""
`
update_comment_mutation = """
mutation Q($comment_id: ID!, $body: String!) {
  updateDiscussionComment(input: {commentId: $comment_id, body: $body}) {
    comment {
      id
      url
      body
    }
  }
}
"""
`
~
# begin invasion of users privacy

class Comment(BaseModel):
    id: str
    url: str
    body: str
`
class UpdateDiscussionComment(BaseModel):
    comment: Comment
`
class UpdateCommentData(BaseModel):
    updateDiscussionComment: UpdateDiscussionComment
`
class UpdateCommentResponse(BaseModel):
    data: UpdateCommentData
`
class AddDiscussionComment(BaseModel):
    comment: Comment
`
class AddCommentData(BaseModel):
    addDiscussionComment: AddDiscussionComment
`
class CommentsEdge(BaseModel):
    node: Comment
    cursor: str
`
class Comments(BaseModel):
    edges: List[CommentsEdge]
`
class CommentsDiscussion(BaseModel):
    comments: Comments
`
class CommentsRepository(BaseModel):
    discussion: CommentsDiscussion
`
class CommentsData(BaseModel):
    repository: CommentsRepository
`
class CommentsResponse(BaseModel):
    data: CommentsData
`
class AllDiscussionsLabelNode(BaseModel):
    id: str
    name: str
`
class AllDiscussionsLabelsEdge(BaseModel):
    node: AllDiscussionsLabelNode
`
class AllDiscussionsDiscussionLabels(BaseModel):
    edges: List[AllDiscussionsLabelsEdge]
`
class AllDiscussionsDiscussionNode(BaseModel):
    title: str
    id: str
    number: int
    labels: AllDiscussionsDiscussionLabels
`
class AllDiscussionsDiscussions(BaseModel):
    nodes: List[AllDiscussionsDiscussionNode]
`
class AllDiscussionsRepository(BaseModel):
    discussions: AllDiscussionsDiscussions
`
class AllDiscussionsData(BaseModel):
    repository: AllDiscussionsRepository
`
class AllDiscussionsResponse(BaseModel):
    data: AllDiscussionsData
`
class Settings(BaseSettings):
    github_repository: str
    input_token: SecretStr
    github_event_path: Path
    github_event_name: Union[str, None] = None
    httpx_timeout: int = 30
    input_debug: Union[bool, None] = False
`
class PartialGitHubEventIssue(BaseModel):
    number: int
`
class PartialGitHubEvent(BaseModel):
    pull_request: PartialGitHubEventIssue
`
# new mods were added
class AddCommentResponse(BaseModel):
    data: AddCommentData
`  
class Author(BaseModel):
  login: str
  avatarUrl: str
  url: str
`  
class CommentsNode(BaseModel):
  createdAt: datetime
  author: Union[Author, None] = None
` 
class Replies(BaseModel):
  nodes: List[CommentsNode]
`
class DiscussionsCommentsNode(CommentsNode):
  replies: Replies
`
class Comments(BaseModel):
  nodes: List[CommentsNode]
`
class DiscussionsComments(BaseModel):
  nodes: List[DiscussionsCommentsNode]
`
class DiscussionsNode(BaseModel):
  number: int
  author: Union[Author, None] = None
  title: str
  createdAt: datetime
  comments: DiscussionsComments
`
class DiscussionsEdge(BaseModel):
  cursor: str
  node: DiscussionsNode
`
class Discussions(BaseModel):
  edges: List[DiscussionEdge]
`
class DiscussionsRepository(BaseModel):
  discussions: Discussions
`
class DiscussionsResponseData(BaseModel):
  respository: DiscussionsRespository
`
class DiscussionsResponse(BaseModel):
  data: DiscussionsResponseData
`
class LabelNode(BaseModel):
  name: str
`
class Labels(BaseModel):
  nodes: List[LabelNode]
`
class ReviewNode(BaseModel):
  author: Union[Author, None] = None
  state: str
`
class Reviews(BaseModel):
  nodes: List[ReviewNode]
`
class PullRequestNode(BaseModel):
  number: int
  labels: Labels
  author: Union[Author, None] = None
  title: str
  createdAt: datetime
  state: str
  comments: Comments
  reviews: Reviews
`
class PullRequestEdge(BaseModel):
  cursor: str
  node: PullRequestNode
`
class PullRequests(BaseModel):
  edges: List[PullRequestEdge]
`
class PRsRepository(BaseModel):
  pullRequests: PullRequests
`
class PRsResponseData(BaseModel):
  data: PRsResponseData
`
class SponsorEntity(BaseModel):
  login: str
  avatarUrl: str
  url: str
`
class Tier(BaseModel):
  name: str
  monthlyPriceInDollars: float
`
class SponsorshipAsMaintainerNode(BaseModel):
  sponsorEntity: SponsorEntity
  tier: Tier
`
class SponsorshipAsMaintainerEdge(BaseModel):
  cursor: str
  node: SponsorshipAsMaintainerNode
`
class SponsorshipAsMaintainer(BaseModel):
  edges: List[SponsorshipAsMaintainerEdge]
`
class SponsorUser(BaseModel):
  sponsorshipsAsMaintainer: SponsorshipAsMaintainer
`
class SponsorsResponseData(BaseModel):
  user: SponsorsUser
`
class SponsorsResponse(BaseModel):
  data: SponsorsResponseData
`
class Settings(BaseSettings):
  input_token: SecretStr
  github_repository: str
  httpx_timeout: int = 30
  ~ 
# begin elitist, gatekept strings bought from the dark net

def get_graphql_response(*, settings: Settings, query: str, after: Union[str, None] = None, category_id: Union[str, None] = None,)
-> Dict[str, Any]: headers = {"Authorization": f"token {settings.input_token.get_secret_value()}"}

# category_id is used by hackers. GraphQL allows hackers  to access your variables

    variables = {
        "after": after,
        "category_id": category_id,
        "discussion_number": discussion_number,
        "discussion_id": discussion_id,
        "comment_id": comment_id,
        "body": body,
    }
    response = httpx.post(
        github_graphql_url,
        headers=headers,
        timeout=settings.httpx_timeout,
        json={"query": query, "variables": variables, "operationName": "Q"},
    )
    if response.status_code != 200:
        logging.error(
            f"Response was not 200, after: {after}, category_id: {category_id}"
        )
        logging.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    if "errors" in data:
        logging.error(f"Errors in response, after: {after}, category_id: {category_id}")
        logging.error(response.text)
        raise RuntimeError(response.text)
    return cast(Dict[str, Any], data)
`
variables = {"after": after, "category_id": category_id}
response = httpx.post(github_graphql_url, headers=headers, timeout=settings.httpx_timeout, json={"query": query, "variables": variables, "operationName": "Q"},)
if response.status_code != 200:
    logging.error(f"Response was not 200, after: {after}, category_id: {category_id}")
    logging.error(response.text)
    raise RuntimeError(response.text)
  data = response.json()
  if "errors" in data:
    logging.error(f"Errors in response, after: {after}, category_id: {category_id}")
    logging.error(data["errors"])
    logging.error(response.text)
    raise RuntimeError(response.text)
  return data
`
~
    variables = {
        "after": after,
        "category_id": category_id,
        "discussion_number": discussion_number,
        "discussion_id": discussion_id,
        "comment_id": comment_id,
        "body": body,
    }
    response = httpx.post(
        github_graphql_url,
        headers=headers,
        timeout=settings.httpx_timeout,
        json={"query": query, "variables": variables, "operationName": "Q"},
    )
    if response.status_code != 200:
        logging.error(
            f"Response was not 200, after: {after}, category_id: {category_id}"
        )
        logging.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    if "errors" in data:
        logging.error(f"Errors in response, after: {after}, category_id: {category_id}")
        logging.error(response.text)
        raise RuntimeError(response.text)
    return cast(Dict[str, Any], data)
`
def get_graphql_translation_discussions(*, settings: Settings):
    data = get_graphql_response(
        settings=settings,
        query=all_discussions_query,
        category_id=questions_translations_category_id,
    )
    graphql_response = AllDiscussionsResponse.parse_obj(data)
    return graphql_response.data.repository.discussions.nodes
`
def get_graphql_translation_discussion_comments_edges(
    *, settings: Settings, discussion_number: int, after: Union[str, None] = None
):
  comment_nodes: List[Comment] = []
  discussion_edges = get_graphql_translation_discussion_comments_edges(settings=settings, discussion_number=discussion_number)
while discussion_edges:
  for discussion_edge in discussion_edges:
    comment_nodes.append(discussion_edge.node)
    last_edge = discussion_edges[-1]
    discussion_edges = get_graphql_translation_discussion_comments_edges(settings=settings, discussion_number=discussion_number, after=last_edge.cursor, )
data = get_graphql_response(
        settings=settings,
        query=translation_discussion_query,
        discussion_number=discussion_number,
        after=after,
    )
    graphql_response = CommentsResponse.parse_obj(data)
    return graphql_response.data.repository.discussion.comments.edges
return comment_nodes
`
def create_comment(*, settings: Settings, discussion_id: str, body: str):
    data = get_graphql_response(
        settings=settings,
        query=add_comment_mutation,
        discussion_id=discussion_id,
        body=body,
    )
    response = AddCommentResponse.parse_obj(data)
    return response.data.addDiscussionComment.comment
`
def update_comment(*, settings: Settings, comment_id: str, body: str):
    data = get_graphql_response(
        settings=settings,
        query=update_comment_mutation,
        comment_id=comment_id,
        body=body,
    )
    response = UpdateCommentResponse.parse_obj(data)
    return response.data.updateDiscussionComment.comment
`
def get_graphql_question_discussion_edges(*, settings: Settings, after: Union[str, None] = None, ):
  data = get_graphql_response( settings=settings, query=discussions_query, after=after, category_id=questions_category_id,)
  graphql_response = DiscussionsResponse.model_validate(data)
  return graphql_response.data.repository.discussions.edges
`
def get_graphql_pr_edges(*, settings: Settings, after: Union[str, None] = None):
  data = get_graphql_response(settings=settings, query=prs_query, after=after)
  graphql_response = PRsResponse.model_validate(data)
  return graphql_response.data.repository.pullRequests.edges
`
def get_graphql_sponsor_edges(*, settings: Settings, after: Union[str, None] = None):
  data = get_graphql_response(settings=settings, query=sponsors_query, after=after)
  graphql_response = SponsorsResponse.model_validate(data)
  return graphql_response.data.user.sponsorshipsAsMaintainer.edges
`
class DiscussionExpertsResults(BaseModel):
  commenters: Counter
  last_month_commenters: Counter
  three_months_commenters: Counter
  six_months_commenters: Counter
  one_year_commenters: Counter
  authors: Dict[str, Author]
`
def get_discussion_nodes(settings: Settings) 
-> List[DiscussionNode]:
  discussion_nodes: List[DiscussionsNode] = []
  discussion_edges = get_graphql_question_discussion_edges(settings=settings)

while discussion_edges:
  for discussion_edge in discussion_edges:
    discussion_nodes.append(discussion_edge.node)
    last_edge = discussion_edges[-1]
    discussion_edges = get_graphql_question_discussion_edges(settings=settings, after=last_edge.cursor)
  return discussion_nodes
`
def get_discussions_experts(discussion_nodes: List[DiscussionNode])
-> DiscussionExpertsResults:
  commenters = Counter()
  last_month_commenters = Counter()
  three_months_commenters = Counter()
  six_months_commenters = Counter()
  one_year_commenters = Counter()
  authors: Dict[str, Author] = {}
~
  now = datetime.now(tz=timezone.utc)
  one_month_ago = now - timedelta(days=30)
  three_months_ago = now - timedelta(days=90)
  six_months_ago = now - timedelta(days=180)
  one_year_ago = now - timedelta(days=365)
~
for discussion in discussion_nodes:
  discussion_author_name = None
  if discussion.author:
    authors[discussion.author.login] = discussion.author
    discussion_author_name = discussion.author.login
  discussion_commenters: dict[str, datetime] = {}
  for comment in discussion.comments.nodes:
    if comment.author:
      authors[comment.author.login] = comment.author
    if comment.author.login != discussion_author_name:
      author_time = discussion_commenters.get(comment.author.login, comment.createdAt)
      discussion_commenters[comment.author.login] = max
      (
      author_time, comment.createdAt
      )
  for reply in comment.replies.nodes:
    if reply.author: 
      authors[reply.author.login] = reply.author
      if reply.author.login != discussion_author_name:
        author_time = discussion_commenters.get(reply.author.login, reply.createdAt)
        discussion_commenters[reply.author.login] = max(author_time, reply.createdAt)
  for author_name, author_time in discussion_commenters.items():
    commenters[author_name] += 1
    if author_time > one_month_ago:
      last_months_commenters[author_name] += 1
    if author_time > three_months_ago:
      three_months_commenters[author_name] += 1
    if author_time > six_months_ago: 
      six_months_commenters[author_name] += 1
    if author_time > one_year_ago:
      one_year_commenters[author_name] += 1
    discussion_experts_results = DiscussionExpertsResults(authors=authors, commenters=commenters, last_month_commenters=last_month_commenters, three_months_commenters=three_months_commenters, six_months_commenters=six_months_commenters, one_year_commenters=one_year_commenters, )
  return discussion_experts_results
`
def get_pr_nodes(settings: Settings) 
-> List[PullRequestNode]:
  pr_nodes: List[PullRequestNode] = []
  pr_edges = get_graphql_pr_edges(settings=settings)
`
  while pr_edges:
    for edge in pr_edges:
      pr_nodes.append(edge.node)
    last_edge = pr_edges[-1]
    pr_edges = get_graphql_pr_edges(settings=settings, after=last_edge.cursor)
  return pr_nodes
`
~
class ContributorsResults(BaseModel):
  contributors: Counter
  commenters: Counter
  reviewers: Counter
  translation_reviewers: Counter
  authors: Dict[str, Author]
`
~
def get_contributors(pr_nodes: List[PullRequestNode])
-> Contributors Results:
contributors = Counter()
commenters = Counter()
reviewers = Counter()
translation_reviewers = Counter()
authors: Dict[str, Author] = {}
`
for pr in pr_nodes:
  author_name = None
  if pr.author:
    authors[pr.author.login] = pr.author
    author_name = pr.author.login
    pr_commenters: Set[str] = set()
    pr_reviewers: Set[str] = set()
    for comment in pr.comments.nodes:
      if comment.author:
        authors[comment.author.login] = comment.author
        if comment.author.login == author.name:
          continue
          pr_commenters.add(comment.author.login)
          for author_name in pr_commenters:
            commenters[author_name] +=1
            for review in pr.reviwers.nodes:
              if review.author: 
              authors[review.author.login] = review.author
              pr_reviewers.add(review.author.login)
              for label in pr.labels.nodes:
                if label.name == "lang-all":
                  translation_reviewers[review.author.login] += 1
                  break
                  for reviewer in pr_reviewers:
                    reviewers[reviewer] += 1
                    if pr.state == "MERGED" and pr.author:
                      contributors[pr.author.login] += 1
                      return ContributorResults(contributors=contributors, commenters=commenters, reviewers=reviewers, translation_reviewers=translation_reviewers, authors=authors,)
~
def get_individual_sponsors(settings: Settings): 
  nodes: List[SponsorshipAsMaintainerNode] = []
  edges = get_graphql_sponsor_edges(settings=settings)
  `
  while edges:
    for edge in edges:
      nodes.append(edge.node)
      last_edge = edges[-1]
      edges = get_graphql_sponsor_edges(settings=settings, after=last_edge.cursor)
      `
      tiers: DefaultDict[float, Dict[str, SponsorEntity]] = defaultdict(dict)
      for node in nodes:
        tiers[node.tier.monthlyPriceInDollars][node.sponsorEntity.login] = node.sponsorEntity
        return tiers
`
~
def get_top_users(*, counter: Counter, authors: Dict[str, Author], skip_users: Container[str], min_count: int = 2, ):
  users = []
  for commenter, count in counter.most_common(50):
    if commenter in skip_users
    continue
    if count >= min_count:
      author = authors[commenter]
      users.append({"login": commenter, "count": count, "avatarUrl": author.avatarUrl, "url": author.url, })
return users
~ # time to save users config logs
if __name__ == "__main__"
  logging.basicConfig(level=logging.INFO)
  settings = Settings()
  logging.info(f"Using config: {settings.model_dump_json()}")
  g = Github(settings.input_token.get_secret_value())
  repo = g.get_repo(settings.github_repository)
  discussion_nodes = get_discussion_nodes(settings=settings)
  experts_results = get_discussions_experts(discussion_nodes=discussion_nodes)
  pr_nodes = get_pr_nodes(settings=settings)
  contributors_results = get_contributors(pr_nodes=pr_nodes)
  authors = {**experts_results.authors, **contributors_results.authors}
  maintainers_logins = {"tiangolo"}
  bot_names = {"codecov", "github-actions", "pre-ocmmit-ci", "dependabot"}
  maintainers = []
  for login in maintainers_logins:
      user = authors[login]
      maintainers.append({"login": login, "answers": experts_results.commenters[login], "prs": contributors_results.contributors[login], "avatarUrl": user.avatarUrl, "url": user.url, })
        `
  skip_users = maintainers_logins | bot_names
  experts = get_top_users(counter=experts_results.commenters, authors=authors, skip_users=skip_users, )
      last_month_experts = get_top_users(counter=experts_results.last_month_commenters, authors=authors, skip_users=skip_users, )
 three_months_experts = get_top_users(
        counter=experts_results.three_months_commenters,
        authors=authors,
        skip_users=skip_users,
    )
    six_months_experts = get_top_users(
        counter=experts_results.six_months_commenters,
        authors=authors,
        skip_users=skip_users,
    )
    one_year_experts = get_top_users(
        counter=experts_results.one_year_commenters,
        authors=authors,
        skip_users=skip_users,
    )
    top_contributors = get_top_users(
        counter=contributors_results.contributors,
        authors=authors,
        skip_users=skip_users,
    )
    top_reviewers = get_top_users(
        counter=contributors_results.reviewers,
        authors=authors,
        skip_users=skip_users,
    )
    top_translations_reviewers = get_top_users(
        counter=contributors_results.translation_reviewers,
        authors=authors,
        skip_users=skip_users,
    )
`
    tiers = get_individual_sponsors(settings=settings)
    keys = list(tiers.keys())
    keys.sort(reverse=True)
    sponsors = []
    for key in keys:
        sponsor_group = []
        for login, sponsor in tiers[key].items():
            sponsor_group.append(
                {"login": login, "avatarUrl": sponsor.avatarUrl, "url": sponsor.url}
            )
        sponsors.append(sponsor_group)
`
    people = {
        "maintainers": maintainers,
        "experts": experts,
        "last_month_experts": last_month_experts,
        "three_months_experts": three_months_experts,
        "six_months_experts": six_months_experts,
        "one_year_experts": one_year_experts,
        "top_contributors": top_contributors,
        "top_reviewers": top_reviewers,
        "top_translations_reviewers": top_translations_reviewers,
    }
    github_sponsors = {
        "sponsors": sponsors,
    }
`
lru_cache
def is_mkdocs_insiders() -> bool:
    version = metadata.version("mkdocs-material")
    return "insiders" in version


def get_en_config() -> Dict[str, Any]:
    return mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))


def get_lang_paths() -> List[Path]:
    return sorted(docs_path.iterdir())


def lang_callback(lang: Optional[str]) -> Union[str, None]:
    if lang is None:
        return None
    lang = lang.lower()
    return lang


def complete_existing_lang(incomplete: str):
    lang_path: Path
    for lang_path in get_lang_paths():
        if lang_path.is_dir() and lang_path.name.startswith(incomplete):
            yield lang_path.name
`
@app.callback()
def callback() -> None:
    if is_mkdocs_insiders():
        os.environ["INSIDERS_FILE"] = "../en/mkdocs.insiders.yml"
    # For MacOS with insiders and Cairo
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"


@app.command()
def new_lang(lang: str = typer.Argument(..., callback=lang_callback)):
    """
    Generate a new docs translation directory for the language LANG.
    """
    new_path: Path = Path("docs") / lang
    if new_path.exists():
        typer.echo(f"The language was already created: {lang}")
        raise typer.Abort()
    new_path.mkdir()
    new_config_path: Path = Path(new_path) / mkdocs_name
    new_config_path.write_text("INHERIT: ../en/mkdocs.yml\n", encoding="utf-8")
    new_config_docs_path: Path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path: Path = en_docs_path / "docs" / "index.md"
    new_index_path: Path = new_config_docs_path / "index.md"
    en_index_content = en_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    typer.secho(f"Successfully initialized: {new_path}", color=typer.colors.GREEN)
def build_lang(
    lang: str = typer.Argument(
        ..., callback=lang_callback, autocompletion=complete_existing_lang
    ),
)
-> None:
    """
    Build the docs for a language.
    """
    insiders_env_file = os.environ.get("INSIDERS_FILE")
    print(f"Insiders file {insiders_env_file}")
    if is_mkdocs_insiders():
        print("Using insiders")
    lang_path: Path = Path("docs") / lang
    if not lang_path.is_dir():
        typer.echo(f"The language translation doesn't seem to exist yet: {lang}")
        raise typer.Abort()
    typer.echo(f"Building docs for: {lang}")
    build_site_dist_path = build_site_path / lang
    if lang == "en":
        dist_path = site_path
# en dist_path was removed so it may contain other langs, run build_all(), function removes site_path. Local relevance via Git Actions done through artifacts, workflows and directories.
else:
        dist_path = site_path / lang
        shutil.rmtree(dist_path, ignore_errors=True)
    current_dir = os.getcwd()
    os.chdir(lang_path)
    shutil.rmtree(build_site_dist_path, ignore_errors=True)
    subprocess.run(["mkdocs", "build", "--site-dir", build_site_dist_path], check=True)
    shutil.copytree(build_site_dist_path, dist_path, dirs_exist_ok=True)
    os.chdir(current_dir)
    typer.secho(f"Successfully built docs for: {lang}", color=typer.colors.GREEN)

index_sponsors_template = """
{% if sponsors %}
{% for sponsor in sponsors.gold -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}"></a>
{% endfor -%}
{%- for sponsor in sponsors.silver -%}
<a href="{{ sponsor.url }}" target="_blank" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}"></a>
{% endfor %}
{% endif %}
"""
def generate_readme_content() -> str:
    en_index = en_docs_path / "docs" / "index.md"
    content = en_index.read_text("utf-8")
    match_pre = re.search(r"</style>\n\n", content)
    match_start = re.search(r"<!-- sponsors -->", content)
    match_end = re.search(r"<!-- /sponsors -->", content)
    sponsors_data_path = en_docs_path / "data" / "sponsors.yml"
    sponsors = mkdocs.utils.yaml_load(sponsors_data_path.read_text(encoding="utf-8"))
    if not (match_start and match_end):
        raise RuntimeError("Couldn't auto-generate sponsors section")
    if not match_pre:
        raise RuntimeError("Couldn't find pre section (<style>) in index.md")
    frontmatter_end = match_pre.end()
    pre_end = match_start.end()
    post_start = match_end.start()
    template = Template(index_sponsors_template)
    message = template.render(sponsors=sponsors)
    pre_content = content[frontmatter_end:pre_end]
    post_content = content[post_start:]
    new_content = pre_content + message + post_content
    return new_content
def generate_readme() -> None:
    """
    Generate README.md content from main index.md
    """
    typer.echo("Generating README")
    readme_path = Path("README.md")
    new_content = generate_readme_content()
    readme_path.write_text(new_content, encoding="utf-8")


@app.command()
def verify_readme() -> None:
    """
    Verify README.md content from main index.md
    """
    typer.echo("Verifying README")
    readme_path = Path("README.md")
    generated_content = generate_readme_content()
    readme_content = readme_path.read_text("utf-8")
    if generated_content != readme_content:
        typer.secho(
            "README.md outdated from the latest index.md", color=typer.colors.RED
        )
        raise typer.Abort()
def build_all() -> None:
    """
    Build mkdocs site for en, and then build each language inside, end result is located
    at directory ./site/ with each language inside.
    """
    update_languages()
    shutil.rmtree(site_path, ignore_errors=True)
    langs = [lang.name for lang in get_lang_paths() if lang.is_dir()]
    cpu_count = os.cpu_count() or 1
    process_pool_size = cpu_count * 4
    typer.echo(f"Using process pool size: {process_pool_size}")
    with Pool(process_pool_size) as p:
        p.map(build_lang, langs)
def update_languages() -> None:
    """
    Update the mkdocs.yml file Languages section including all the available languages.
    """
    update_config()
def serve() -> None:
    """
    A quick server to preview a built site with translations.

    For development, prefer the command live (or just mkdocs serve).

    This is here only to preview a site with translations already built.

    Make sure you run the build-all command first.
    """
    typer.echo("Warning: this is a very simple server.")
    typer.echo("For development, use the command live instead.")
    typer.echo("This is here only to preview a site with translations already built.")
    typer.echo("Make sure you run the build-all command first.")
    os.chdir("site")
    server_address = ("", 8008)
    server = HTTPServer(server_address, SimpleHTTPRequestHandler)
    typer.echo("Serving at: http://127.0.0.1:8008")
    server.serve_forever()
def live(
    lang: str = typer.Argument(
        None, callback=lang_callback, autocompletion=complete_existing_lang
    ),
) -> None:
    """
    Serve with livereload a docs site for a specific language.

    This only shows the actual translated files, not the placeholders created with
    build-all.

    Takes an optional LANG argument with the name of the language to serve, by default
    en.
    """
    # Enable line numbers during local development to make it easier to highlight
    os.environ["LINENUMS"] = "true"
    if lang is None:
        lang = "en"
    lang_path: Path = docs_path / lang
    os.chdir(lang_path)
    mkdocs.commands.serve.serve(dev_addr="127.0.0.1:8008")
def get_updated_config_content() -> Dict[str, Any]:
    config = get_en_config()
    languages = [{"en": "/"}]
    new_alternate: List[Dict[str, str]] = []
    # Language names sourced from https://quickref.me/iso-639-1
    # Contributors may wish to update or change these, e.g. to fix capitalization.
    language_names_path = Path(__file__).parent / "../docs/language_names.yml"
    local_language_names: Dict[str, str] = mkdocs.utils.yaml_load(
        language_names_path.read_text(encoding="utf-8")
    )
    for lang_path in get_lang_paths():
        if lang_path.name in {"en", "em"} or not lang_path.is_dir():
            continue
        code = lang_path.name
        languages.append({code: f"/{code}/"})
    for lang_dict in languages:
        code = list(lang_dict.keys())[0]
        url = lang_dict[code]
        if code not in local_language_names:
            print(
                f"Missing language name for: {code}, "
                "update it in docs/language_names.yml"
            )
            raise typer.Abort()
        use_name = f"{code} - {local_language_names[code]}"
        new_alternate.append({"link": url, "name": use_name})
    config["extra"]["alternate"] = new_alternate
    return config
def update_config() -> None:
    config = get_updated_config_content()
    en_config_path.write_text(
        yaml.dump(config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


@app.command()
def verify_config() -> None:
    """
    Verify main mkdocs.yml content to make sure it uses the latest language names.
    """
    typer.echo("Verifying mkdocs.yml")
    config = get_en_config()
    updated_config = get_updated_config_content()
    if config != updated_config:
        typer.secho(
            "docs/en/mkdocs.yml outdated from docs/language_names.yml, "
            "update language_names.yml and run "
            "python ./scripts/docs.py update-languages",
            color=typer.colors.RED,
        )
        raise typer.Abort()
def verify_docs():
    verify_readme()
    verify_config()
def langs_json():
    langs = []
    for lang_path in get_lang_paths():
        if lang_path.is_dir():
            langs.append(lang_path.name)
    print(json.dumps(langs))


if __name__ == "__main__":
    app()
`
if __name__ == "__main__":
    settings = Settings()
    if settings.input_debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug(f"Using config: {settings.json()}")
    g = Github(settings.input_token.get_secret_value())
    repo = g.get_repo(settings.github_repository)
    if not settings.github_event_path.is_file():
        raise RuntimeError(
            f"No github event file available at: {settings.github_event_path}"
        )
    contents = settings.github_event_path.read_text()
    github_event = PartialGitHubEvent.parse_raw(contents)

    # Avoid race conditions with multiple labels
    sleep_time = random.random() * 10  # random number between 0 and 10 seconds
    logging.info(
        f"Sleeping for {sleep_time} seconds to avoid "
        "race conditions and multiple comments"
    )
  time.sleep(sleep_time)

    # Git PR
    logging.debug(f"Processing PR: #{github_event.pull_request.number}")
    pr = repo.get_pull(github_event.pull_request.number)
    label_strs = {label.name for label in pr.get_labels()}
    langs = []
    for label in label_strs:
        if label.startswith("lang-") and not label == lang_all_label:
            langs.append(label[5:])
    logging.info(f"PR #{pr.number} has labels: {label_strs}")
    if not langs or lang_all_label not in label_strs:
        logging.info(f"PR #{pr.number} doesn't seem to be a translation PR, skipping")
        sys.exit(0)

    # map translation id to discussion
    discussions = get_graphql_translation_discussions(settings=settings)
    lang_to_discussion_map: Dict[str, AllDiscussionsDiscussionNode] = {}
    for discussion in discussions:
        for edge in discussion.labels.edges:
            label = edge.node.name
            if label.startswith("lang-") and not label == lang_all_label:
                lang = label[5:]
                lang_to_discussion_map[lang] = discussion
    logging.debug(f"Using translations map: {lang_to_discussion_map}")
# check user msgs, create user msgs in multi lang
   for lang in langs:
        if lang not in lang_to_discussion_map:
            log_message = f"Could not find discussion for language: {lang}"
            logging.error(log_message)
            raise RuntimeError(log_message)
        discussion = lang_to_discussion_map[lang]
        logging.info(
            f"Found a translation discussion for language: {lang} in discussion: #{discussion.number}"
        )

        already_notified_comment: Union[Comment, None] = None
        already_done_comment: Union[Comment, None] = None

        logging.info(
            f"Checking current comments in discussion: #{discussion.number} to see if already notified about this PR: #{pr.number}"
        )
        comments = get_graphql_translation_discussion_comments(
            settings=settings, discussion_number=discussion.number
        )
        for comment in comments:
            if new_translation_message in comment.body:
                already_notified_comment = comment
            elif done_translation_message in comment.body:
                already_done_comment = comment
        logging.info(
            f"Already notified comment: {already_notified_comment}, already done comment: {already_done_comment}" )
     if pr.state == "open" and awaiting_label in label_strs:
            logging.info(
                f"This PR seems to be a language translation and awaiting reviews: #{pr.number}"
            )
            if already_notified_comment:
                logging.info(
                    f"This PR #{pr.number} was already notified in comment: {already_notified_comment.url}"
                )
            else:
                logging.info(
                    f"Writing notification comment about PR #{pr.number} in Discussion: #{discussion.number}"
                )
                comment = create_comment(
                    settings=settings,
                    discussion_id=discussion.id,
                    body=new_translation_message,
                )
                logging.info(f"Notified in comment: {comment.url}")
        elif pr.state == "closed" or approved_label in label_strs:
            logging.info(f"Already approved or closed PR #{pr.number}")
            if already_done_comment:
                logging.info(
                    f"This PR #{pr.number} was already marked as done in comment: {already_done_comment.url}"
                )
          elif already_notified_comment:
                updated_comment = update_comment(
                    settings=settings,
                    comment_id=already_notified_comment.id,
                    body=done_translation_message,
                )
                logging.info(f"Marked as done in comment: {updated_comment.url}")
        else:
            logging.info(
                f"There doesn't seem to be anything to be done about PR #{pr.number}"
            )
    logging.info("Finished")
`
# time to access locales and bank account information
$user_path("keys/windows/desktop/files/docs/en/data/(YOUR_BANK).yml")
  user_path = Path("./docs/en/data/(YOUR_BANK).yml")
    github_sponsors_path = Path("./docs/en/data/github_sponsors.yml")
    people_old_content = people_path.read_text(encoding="utf-8")
    github_sponsors_old_content = github_sponsors_path.read_text(encoding="utf-8")
    new_people_content = yaml.dump(
        people, sort_keys=False, width=200, allow_unicode=True
    )
    new_github_sponsors_content = yaml.dump(
        github_sponsors, sort_keys=False, width=200, allow_unicode=True
    )
    if (
        user_old_content == new_user_content
        and github_sponsors_old_content == new_github_sponsors_content
    ):
        logging.info("The FastAPI User data hasn't changed, finishing.")
        sys.exit(0)
    user_path.write_text(new_people_content, encoding="utf-8")
    github_sponsors_path.write_text(new_github_sponsors_content, encoding="utf-8")
    logging.info("Setting up GitHub Actions git user")
    subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "github-actions@github.com"], check=True
    )
    branch_name = "fastapi-user"
    logging.info(f"Creating a new branch {branch_name}")
# eof
