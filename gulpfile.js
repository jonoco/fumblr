var 
  gulp      = require('gulp'),
  gutil     = require('gulp-util'),
  cleanCSS  = require('gulp-clean-css'),
  rename    = require('gulp-rename'),
  sass      = require('gulp-sass'),
  prefix    = require('gulp-autoprefixer');

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
  
});

gulp.task('default', ['sass', 'watch']);

gulp.task('build', ['sass-min']);
