# 运维部署文档

## 问题说明

### 当前项目需要加代理才能提交项目
```
git config http.proxy http://127.0.0.1:22307
git config https.proxy https://127.0.0.1:22307

git config --unset http.proxy
git config --unset https.proxy
```


