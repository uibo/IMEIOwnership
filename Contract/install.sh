#!/bin/bash

while read -r line; do
  forge install "$line"
done < foundry-deps.txt
