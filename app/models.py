"""Database models."""
from datetime import datetime
from app.extensions import db
from flask_login import UserMixin


# User Model DATABASE
class User(db.Model, UserMixin):
    """User model."""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Profile Information
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    
    # Social Media Links
    twitter = db.Column(db.String(50), nullable=True)
    github = db.Column(db.String(50), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='author_user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    
    def get_profile_image(self):
        """Get Gravatar profile image based on email."""
        import hashlib
        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200'
    
    def get_comment_count(self):
        """Get total number of comments by this user."""
        return Comment.query.filter_by(user_id=self.id).count()
    
    def get_likes_received_count(self):
        """Get total likes received on user's posts and comments."""
        total = 0
        
        # Count likes on posts
        for post in self.posts:
            total += post.get_like_count()
        
        # Count likes on comments
        comments = Comment.query.filter_by(user_id=self.id).all()
        for comment in comments:
            total += comment.get_like_count()
        
        return total
    
    def get_likes_given_count(self):
        """Get total likes given by user."""
        return Like.query.filter_by(user_id=self.id).count()
    
    def __repr__(self):
        return f'<User {self.username}>'


# POST MODEL DATABASE
class Post(db.Model):
    """Post model."""
    
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False, default='Nazrul Haque')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)
    
    def get_comment_count(self):
        """Get total number of comments (including replies)."""
        return Comment.query.filter_by(post_id=self.id).count()
    
    def get_like_count(self):
        """Get total number of likes."""
        return Like.query.filter_by(post_id=self.id).count()
    
    def is_liked_by(self, user):
        """Check if user has liked this post."""
        if not user.is_authenticated:
            return False
        return Like.query.filter_by(post_id=self.id, user_id=user.id).first() is not None
    
    def get_likers(self):
        """Get list of users who liked this post."""
        likes = Like.query.filter_by(post_id=self.id).all()
        return [like.user for like in likes]
    
    def __repr__(self):
        return f'<Post {self.title}>'


# COMMENT MODEL DATABASE
class Comment(db.Model):
    """Comment model."""
    
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    
    # Self-referential relationship for replies
    replies = db.relationship('Comment',
                            backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic')
    likes = db.relationship('Like', backref='comment', lazy=True)
    
    def get_like_count(self):
        """Get total number of likes."""
        return Like.query.filter_by(comment_id=self.id).count()
    
    def is_liked_by(self, user):
        """Check if user has liked this comment."""
        if not user.is_authenticated:
            return False
        return Like.query.filter_by(comment_id=self.id, user_id=user.id).first() is not None
    
    def get_likers(self):
        """Get list of users who liked this comment."""
        likes = Like.query.filter_by(comment_id=self.id).all()
        return [like.user for like in likes]
    
    def __repr__(self):
        return f'<Comment by {self.author.username}>'


# LIKE MODEL
class Like(db.Model):
    """Like model."""
    
    __tablename__ = 'like'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Like by User {self.user_id}>'