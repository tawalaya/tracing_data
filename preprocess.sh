#!/bin/sh
experimentes=( 'failiure' 'normal' )

for f in "${experimentes[@]}"
do
    cd "./data/$f"

    #this can be very unsave....
    rm activations/*.json

    for i in raw/*list*_result.json
    do
        /usr/bin/cat $i | jq   '.[]' | jq   '.[]' | jq -s '.' > "activations/pu_${i#raw/activation_list_}"
    done

    for i in  raw/fetchImages*_result.json
    do
        /usr/bin/cat $i | jq   '.[]' | jq   '.[]' | jq -s '.' > "activations/fi_${i#raw/fetchImages_}"
    done

    cd ../..

done

