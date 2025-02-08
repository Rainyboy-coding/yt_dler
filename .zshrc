
# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/dream/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/dream/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/dream/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/dream/Downloads/google-cloud-sdk/completion.zsh.inc'; fi
eval "$(/opt/homebrew/bin/brew shellenv)"
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles
export PATH="/Users/dream/Downloads:$PATH"
