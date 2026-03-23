"""Admin routes."""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import User, Post, Comment, Like


@admin_bp.route("/")
@login_required
def admin_dashboard():
    """Admin dashboard - only for admins."""
    if not current_user.is_admin:
        flash('Admin access required!', 'danger')
        return redirect(url_for('main.home'))
    
    # Get statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_likes = Like.query.count()
    
    # Get recent items
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                          total_users=total_users,
                          total_posts=total_posts,
                          total_comments=total_comments,
                          total_likes=total_likes,
                          recent_posts=recent_posts,
                          recent_users=recent_users,
                          recent_comments=recent_comments)