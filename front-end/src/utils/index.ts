import router from "@/router"


const getSourceName = (source: string) => {
  switch (source) {
    case 'baidu':
      return '百度'
    case 'bilibili':
      return '哔哩哔哩'
    case 'douyin':
      return '抖音'
    case 'douban-group':
      return '豆瓣小组'
    case 'douban-movie':
      return '豆瓣电影'
    case 'hupu':
      return '虎扑'
    case 'sina':
      return '新浪'
    case 'tieba':
      return '贴吧'
    case 'toutiao':
      return '头条'
    case 'weibo':
      return '微博'
    case 'zhihu':
      return '知乎'
    case 'qq-news':
      return '腾讯新闻'
    case 'sina-news':
      return '新浪新闻'
    case 'netease-news':
      return '网易新闻'
    case 'thepaper':
      return '澎湃新闻'
    case 'zhihu-daily':
      return '知乎日报'

    case 'kuaishou':
      return '快手'
    case 'red':
      return '小红书'
    default:
      return source
  }
}

const getStatusName = (status: number) => {
  switch (status) {
    case 0:
      return '待确认'
    case 1:
      return '已确认'
    case 2:
      return '生成中'
    case 3:
      return '可发布'
    case 4:
      return '已使用'
    default:
      return status
  }
}

const visitUrlAtBlank = (url: string) => {
  console.log(url)
  window.open(url, '_blank');
}

const visitHomePath = () => {
  router.push('/')
}

export { getSourceName, getStatusName, visitUrlAtBlank, visitHomePath }