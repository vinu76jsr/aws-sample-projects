"""
Flask Web Application for Polls.

This provides a web interface similar to Django's polls tutorial.
Routes mirror Django's URL patterns for familiarity.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import Poll, Choice, batch_create_poll_with_choices
from db import table_exists, create_table

app = Flask(__name__)
app.secret_key = "dev-secret-key"


@app.before_request
def ensure_table():
    """Ensure DynamoDB table exists before handling requests."""
    if not hasattr(app, "_table_checked"):
        if not table_exists():
            create_table()
        app._table_checked = True


@app.route("/")
def index():
    """
    Display list of recent polls.
    Similar to Django's polls:index view.
    """
    polls = Poll.get_recent(limit=10)
    return render_template("index.html", polls=polls)


@app.route("/polls/")
def poll_list():
    """Display all polls."""
    polls = Poll.get_all()
    return render_template("poll_list.html", polls=polls)


@app.route("/polls/<poll_id>/")
def poll_detail(poll_id):
    """
    Display poll detail with voting form.
    Similar to Django's polls:detail view.
    """
    poll = Poll.get(poll_id)
    if not poll:
        flash("Poll not found", "error")
        return redirect(url_for("index"))

    choices = poll.get_choices()
    return render_template("detail.html", poll=poll, choices=choices)


@app.route("/polls/<poll_id>/vote/", methods=["POST"])
def vote(poll_id):
    """
    Handle voting.
    Similar to Django's polls:vote view.
    """
    poll = Poll.get(poll_id)
    if not poll:
        flash("Poll not found", "error")
        return redirect(url_for("index"))

    choice_id = request.form.get("choice")
    if not choice_id:
        flash("You didn't select a choice.", "error")
        return redirect(url_for("poll_detail", poll_id=poll_id))

    choice = Choice.get(poll_id, choice_id)
    if not choice:
        flash("Invalid choice", "error")
        return redirect(url_for("poll_detail", poll_id=poll_id))

    # Atomic vote increment
    choice.vote()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("poll_results", poll_id=poll_id))


@app.route("/polls/<poll_id>/results/")
def poll_results(poll_id):
    """
    Display poll results.
    Similar to Django's polls:results view.
    """
    poll = Poll.get(poll_id)
    if not poll:
        flash("Poll not found", "error")
        return redirect(url_for("index"))

    choices = poll.get_choices()
    total_votes = sum(c.votes for c in choices)

    return render_template(
        "results.html",
        poll=poll,
        choices=choices,
        total_votes=total_votes
    )


@app.route("/polls/create/", methods=["GET", "POST"])
def create_poll():
    """Create a new poll with choices."""
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        choices_text = request.form.get("choices", "").strip()

        if not question:
            flash("Question is required", "error")
            return render_template("create.html")

        if not choices_text:
            flash("At least one choice is required", "error")
            return render_template("create.html")

        # Parse choices (one per line)
        choices = [c.strip() for c in choices_text.split("\n") if c.strip()]

        if len(choices) < 2:
            flash("At least two choices are required", "error")
            return render_template("create.html")

        # Create poll with batch operation
        poll = batch_create_poll_with_choices(question, choices)
        flash(f"Poll created successfully!", "success")
        return redirect(url_for("poll_detail", poll_id=poll.poll_id))

    return render_template("create.html")


@app.route("/polls/<poll_id>/delete/", methods=["POST"])
def delete_poll(poll_id):
    """Delete a poll."""
    poll = Poll.get(poll_id)
    if poll:
        poll.delete()
        flash("Poll deleted successfully", "success")
    return redirect(url_for("index"))


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Server error"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)