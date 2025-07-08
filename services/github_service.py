from github import Github, InputGitTreeElement
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging

logger = setup_logging(__file__)

github_token = get_secrets(["github/pat_obsidian"])

g = Github(github_token)
repository_name = "obsidian"
branch_name = "main"


def add_files_to_repository(
	list_of_files,
	commit_message,
	subpath,
	repository_name="obsidian",
	branch_name="main",
):
	repo = g.get_repo(g.get_user().login + "/" + repository_name)
	logger.info(f"repo: {repo}")

	blobs = []
	for file in list_of_files:
		blob = repo.create_git_blob(
			content=file["content"],
			encoding="utf-8",
		)
		blobs.append(blob)
		logger.info(f"Created blob for {file['filename']}: {blob}")

	tree_elements = [
		InputGitTreeElement(
			path=subpath + file["filename"],
			mode="100644",
			type="blob",
			sha=blob.sha,
		)
		for file, blob in zip(list_of_files, blobs)
	]

	base_tree = repo.get_git_tree(sha=repo.get_branch(branch_name).commit.sha)
	new_tree = repo.create_git_tree(tree=tree_elements, base_tree=base_tree)
	logger.info(f"new_tree: {new_tree}")

	commit = repo.create_git_commit(
		message=commit_message,
		tree=new_tree,
		parents=[repo.get_git_commit(repo.get_branch(branch_name).commit.sha)],
	)
	logger.info(f"commit: {commit}")

	hello_world_ref = repo.get_git_ref(ref="heads/" + branch_name)
	hello_world_ref.edit(sha=commit.sha)
	logger.info("DONE")
