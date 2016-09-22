var 
  gulp      = require('gulp'),
  gutil     = require('gulp-util'),
  cleanCSS  = require('gulp-clean-css'),
  rename    = require('gulp-rename'),
  sass      = require('gulp-sass'),
  babel     = require('gulp-babel'),
  prefix    = require('gulp-autoprefixer'),
  uglify    = require('gulp-uglify'),
  livereload = require('gulp-livereload');

gulp.task('js', function() {
  gulp.src('fumblr/src/js/main.js')
    .pipe(babel())
    .pipe(gulp.dest('fumblr/static/js'));
});

gulp.task('js-min', function() {
  gulp.src('fumblr/src/js/main.js')
    .pipe(babel())
    .pipe(uglify())
    .pipe(gulp.dest('fumblr/static/js'));
});

gulp.task('sass', function() {
  gulp.src('fumblr/src/stylesheets/main.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(prefix())
    .pipe(rename('main.css'))
    .pipe(gulp.dest('fumblr/static/css'));
});

gulp.task('sass-min', function() {
  gulp.src('fumblr/src/stylesheets/main.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(prefix())
    .pipe(cleanCSS())
    .pipe(rename('main.css'))
    .pipe(gulp.dest('fumblr/static/css'));
});

gulp.task('watch', function() {
  gulp.watch('fumblr/src/stylesheets/*/*.scss', ['sass']);
  gulp.watch('fumblr/src/js/*.js', ['js']);
});

gulp.task('default', ['watch', 'js', 'sass']);
gulp.task('build', ['js-min', 'sass-min']);
