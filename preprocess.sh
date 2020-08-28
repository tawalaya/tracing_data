#!/bin/sh
rm data/activations/*

for i in data/raw/*list*_result.json
do
    /usr/bin/cat $i | jq   '.[]' | jq   '.[]' | jq -s '.' > "data/activations/${i#data/raw/}"
done

for i in data/raw/fetchImages*_result.json
do
    /usr/bin/cat $i | jq   '.[]' | jq   '.[]' | jq -s '.' > "data/activations/${i#data/raw/}"
done
# files=( 'data/raw/baseline_result.json' 'data/raw/provider_side_result.json' 'data/raw/function_side_result.json' )
# for i in "${files[@]}"
# do
#     /usr/bin/cat $i | jq   '.[]' | jq -s '.' > "data/activations/${i#data/raw/}"
# done

