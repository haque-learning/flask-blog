"""Main application routes."""
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from math import ceil
from app.main import main_bp
from app.extensions import db, limiter
from app.models import Post, Comment, Like, User


# ========== HOME & STATIC PAGES ==========

@main_bp.route("/")
def home():
    """Homepage with stats and recent posts."""
    from app.models import User, Post, Comment, Like
    
    blog_name = "Nazrul's Blog"
    
    # Get statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    # Get 3 most recent posts
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template("home.html",
                          name=blog_name,
                          total_users=total_users,
                          total_posts=total_posts,
                          total_comments=total_comments,
                          total_likes=total_likes,
                          recent_posts=recent_posts)


@main_bp.route("/about")
def about():
    """About page."""
    author = "Nazrul Haque"
    email = "6hZlO@example.com"
    age = 45
    return render_template("about.html", author=author, email=email, age=age)


@main_bp.route("/contact")
def contact():
    """Contact page."""
    author = "Nazrul Haque"
    email = "6hZlO@example.com"
    return render_template("contact.html", author=author, email=email)


# ========== POST ROUTES ==========

@main_bp.route("/post")
def posts():
    """Display all posts with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    # Paginate posts
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    posts = pagination.items
    
    return render_template('posts.html', posts=posts, pagination=pagination)


@main_bp.route("/post/<int:post_id>")
def view_post(post_id):
    """View a single post with comments."""
    post = Post.query.get_or_404(post_id)
    
    # Get all top-level comments (not replies)
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
                            .order_by(Comment.created_at.desc())\
                            .all()
    
    # Get comment count
    comment_count = post.get_comment_count()
    
    return render_template('view_post.html',
                          post=post,
                          comments=comments,
                          comment_count=comment_count)


@main_bp.route("/post/new", methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post (login required)."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Create post linked to current user
        new_post = Post(
            title=title,
            content=content,
            author=current_user.username,
            user_id=current_user.id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Your post has been published!', 'success')
        return redirect(url_for('main.view_post', post_id=new_post.id))
    
    return render_template('create_post.html')


@main_bp.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a post (must be author or admin)."""
    post = Post.query.get_or_404(post_id)
    
    # Check if current user is the author OR an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You can only edit your own posts!', 'danger')
        return redirect(url_for('main.posts'))
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        
        flash('Post has been updated!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))
    
    return render_template('edit_post.html', post=post)


@main_bp.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete a post (must be author or admin)."""
    post = Post.query.get_or_404(post_id)
    
    # Check if current user is the author OR an admin
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own posts!', 'danger')
        return redirect(url_for('main.posts'))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post has been deleted!', 'success')
    return redirect(url_for('main.posts'))


@main_bp.route("/post/popular")
def popular_posts():
    """Show posts sorted by popularity with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    # Get all posts and sort by likes
    all_posts = Post.query.all()
    posts_sorted = sorted(all_posts, key=lambda p: p.get_like_count(), reverse=True)
    
    # Manual pagination for sorted list
    total = len(posts_sorted)
    start = (page - 1) * per_page
    end = start + per_page
    posts = posts_sorted[start:end]
    
    # Create a simple pagination object
    class SimplePagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = ceil(total / per_page)
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = SimplePagination(page, per_page, total, posts)
    
    return render_template('posts.html', posts=posts, pagination=pagination)


@main_bp.route("/my-posts")
@login_required
def my_posts():
    """User's personal posts dashboard."""
    # Get all posts by current user
    user_posts = Post.query.filter_by(user_id=current_user.id)\
                            .order_by(Post.created_at.desc())\
                            .all()
    
    # Calculate statistics
    total_posts = len(user_posts)
    
    # Get date of first post
    first_post_date = user_posts[-1].created_at if user_posts else None
    
    # Calculate total words across all posts
    total_words = sum(len(post.content.split()) for post in user_posts)
    
    return render_template('my_posts.html',
                          posts=user_posts,
                          total_posts=total_posts,
                          first_post_date=first_post_date,
                          total_words=total_words)


# ========== COMMENT ROUTES ==========

@main_bp.route("/post/<int:post_id>/comment", methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def add_comment(post_id):
    """Add a comment to a post."""
    post = Post.query.get_or_404(post_id)
    
    content = request.form.get('content')
    parent_id = request.form.get('parent_id')
    
    if not content or not content.strip():
        flash('Comment cannot be empty!', 'danger')
        return redirect(url_for('main.view_post', post_id=post_id))
    
    # Create new comment
    new_comment = Comment(
        content=content.strip(),
        user_id=current_user.id,
        post_id=post_id,
        parent_id=int(parent_id) if parent_id else None
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('main.view_post', post_id=post_id))


@main_bp.route("/comment/<int:comment_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    """Edit a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user owns this comment or is admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You can only edit your own comments!', 'danger')
        return redirect(url_for('main.view_post', post_id=comment.post_id))
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content or not content.strip():
            flash('Comment cannot be empty!', 'danger')
            return redirect(url_for('main.view_post', post_id=comment.post_id))
        
        # Update comment
        comment.content = content.strip()
        comment.edited_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('main.view_post', post_id=comment.post_id))
    
    # GET request - show edit form
    return render_template('edit_comment.html', comment=comment)


@main_bp.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user owns this comment or is admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You can only delete your own comments!', 'danger')
        return redirect(url_for('main.view_post', post_id=comment.post_id))
    
    post_id = comment.post_id
    
    # Delete all replies first (cascade delete)
    Comment.query.filter_by(parent_id=comment.id).delete()
    
    # Delete the comment
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('main.view_post', post_id=post_id))


# ========== LIKE ROUTES ==========

@main_bp.route("/post/<int:post_id>/like", methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def like_post(post_id):
    """Like or unlike a post."""
    post = Post.query.get_or_404(post_id)
    
    # Check if already liked
    existing_like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        return {'liked': False, 'count': post.get_like_count()}
    else:
        # Like
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        return {'liked': True, 'count': post.get_like_count()}


@main_bp.route("/comment/<int:comment_id>/like", methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def like_comment(comment_id):
    """Like or unlike a comment."""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if already liked
    existing_like = Like.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        return {'liked': False, 'count': comment.get_like_count()}
    else:
        # Like
        new_like = Like(user_id=current_user.id, comment_id=comment_id)
        db.session.add(new_like)
        db.session.commit()
        return {'liked': True, 'count': comment.get_like_count()}


# ========== SEARCH ROUTES ==========

@main_bp.route("/search")
@limiter.limit("20 per minute")
def search():
    """Search posts by title and content with pagination."""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    if query:
        # Search in both title and content (case-insensitive)
        search_pattern = f"%{query}%"
        pagination = Post.query.filter(
            db.or_(
                Post.title.ilike(search_pattern),
                Post.content.ilike(search_pattern)
            )
        ).order_by(Post.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        posts = pagination.items
    else:
        posts = []
        pagination = None
    
    return render_template('search_results.html', posts=posts, query=query, pagination=pagination)


# ========== USER PROFILE ROUTES ==========

@main_bp.route("/user/<string:username>")
def user_profile(username):
    """View a user's profile."""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get all posts by this user, newest first
    user_posts = Post.query.filter_by(user_id=user.id)\
                            .order_by(Post.created_at.desc())\
                            .all()
    
    # Count posts
    post_count = len(user_posts)
    
    return render_template('user_profile.html',
                          user=user,
                          posts=user_posts,
                          post_count=post_count)


@main_bp.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        # Get form data
        current_user.bio = request.form.get('bio', '')
        current_user.location = request.form.get('location', '')
        current_user.website = request.form.get('website', '')
        current_user.twitter = request.form.get('twitter', '')
        current_user.github = request.form.get('github', '')
        current_user.linkedin = request.form.get('linkedin', '')
        
        # Save to database
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.user_profile', username=current_user.username))
    
    # GET request - show the form with current data
    return render_template('edit_profile.html')


# ========== UTILITY ROUTES ==========

@main_bp.route("/add-sample-posts")
def add_sample_posts():
    """Add some sample posts to the database."""
    
    # Check if posts already exist
    existing_posts = Post.query.all()
    if len(existing_posts) > 0:
        return "Posts already exist! Go to <a href='/'>home</a>"
    
    # Create sample posts
    post1 = Post(
        title="My First Blog Post",
        content="This is my very first blog post! I'm learning Flask and it's amazing. I can now create dynamic web applications with Python!",
        author="Nazrul Haque"
    )
    
    post2 = Post(
        title="Learning Flask is Fun",
        content="Flask is such a great framework for beginners. It's simple, yet powerful. Today I learned about routes, templates, and databases!",
        author="Other User"
    )
    
    post3 = Post(
        title="Python Tips for Beginners",
        content="Here are some Python tips: 1) Use virtual environments, 2) Write clean code, 3) Practice every day, 4) Build real projects!",
        author="Nazrul Haque"
    )
    
    # Add to database session
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    
    # Commit to database (save permanently)
    db.session.commit()
    
    return "✅ 3 sample posts added! <a href='/post'>View posts</a>"