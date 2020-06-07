# Usage: ./make_thumbnails.sh img/news/hackersongscassette/*.jpg
for fnm in ${BASH_ARGV[*]} ; do
    convert -thumbnail 225 "$fnm" `echo $fnm | sed 's/.jpg/_thumb.jpg/'`
done
