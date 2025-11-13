import React, { useState, useEffect, useRef } from 'react'
import { Input, Button, AutoComplete, Space, Tag, Spin } from 'antd'
import {
  SearchOutlined,
  AudioOutlined,
  CameraOutlined,
  SettingOutlined,
  HistoryOutlined,
  ClearOutlined
} from '@ant-design/icons'
import { useDebounce } from 'react-use'

const { Search } = Input

export interface SearchSuggestion {
  text: string
  type: 'history' | 'popular' | 'auto'
  highlight?: string
}

export interface SearchInputProps {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onSearch?: (value: string, options?: SearchOptions) => void
  onSuggestionSelect?: (suggestion: SearchSuggestion) => void
  loading?: boolean
  suggestions?: SearchSuggestion[]
  disabled?: boolean
  size?: 'small' | 'middle' | 'large'
  showHistory?: boolean
  showVoiceInput?: boolean
  showImageInput?: boolean
  showAdvancedOptions?: boolean
  className?: string
  style?: React.CSSProperties
}

export interface SearchOptions {
  useAI?: boolean
  filters?: string[]
  sortBy?: string
  dateRange?: [string, string]
}

const SearchInput: React.FC<SearchInputProps> = ({
  placeholder = '输入搜索关键词，支持语义搜索...',
  value = '',
  onChange,
  onSearch,
  onSuggestionSelect,
  loading = false,
  suggestions = [],
  disabled = false,
  size = 'large',
  showHistory = true,
  showVoiceInput = true,
  showImageInput = true,
  showAdvancedOptions = true,
  className = '',
  style = {}
}) => {
  const [inputValue, setInputValue] = useState(value)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [searchOptions, setSearchOptions] = useState<SearchOptions>({
    useAI: true,
    filters: [],
    sortBy: 'relevance'
  })
  const [debouncedValue, setDebouncedValue] = useState('')
  const inputRef = useRef<any>(null)

  // 防抖处理
  useDebounce(
    () => {
      setDebouncedValue(inputValue)
    },
    500,
    [inputValue]
  )

  // 同步外部value
  useEffect(() => {
    setInputValue(value)
  }, [value])

  // 搜索建议处理
  useEffect(() => {
    if (debouncedValue.trim().length > 0 && onChange) {
      onChange(debouncedValue)
    }
  }, [debouncedValue])

  const handleSearch = (searchValue: string = inputValue) => {
    if (searchValue.trim().length === 0) return

    if (onSearch) {
      onSearch(searchValue, searchOptions)
    }

    // 保存到搜索历史
    saveToHistory(searchValue)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleSuggestionSelect = (value: string, option: any) => {
    const suggestion = suggestions.find(s => s.text === value)
    if (suggestion && onSuggestionSelect) {
      onSuggestionSelect(suggestion)
    }
    setInputValue(value)
  }

  const saveToHistory = (query: string) => {
    try {
      const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
      const newHistory = [query, ...history.filter((h: string) => h !== query)].slice(0, 50)
      localStorage.setItem('searchHistory', JSON.stringify(newHistory))
    } catch (error) {
      console.error('保存搜索历史失败:', error)
    }
  }

  const getHistorySuggestions = (): SearchSuggestion[] => {
    try {
      const history = JSON.parse(localStorage.getItem('searchHistory') || '[]')
      return history.slice(0, 10).map((item: string) => ({
        text: item,
        type: 'history' as const
      }))
    } catch (error) {
      return []
    }
  }

  const clearHistory = () => {
    try {
      localStorage.removeItem('searchHistory')
    } catch (error) {
      console.error('清除搜索历史失败:', error)
    }
  }

  const allSuggestions = [
    ...getHistorySuggestions(),
    ...suggestions
  ]

  // 格式化建议选项
  const formattedOptions = allSuggestions.map((suggestion, index) => ({
    value: suggestion.text,
    label: (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>{suggestion.text}</span>
        {suggestion.type === 'history' && (
          <Tag size="small" color="blue" style={{ marginLeft: 8 }}>
            历史搜索
          </Tag>
        )}
      </div>
    ),
    key: `${suggestion.type}-${index}`
  }))

  const handleVoiceInput = () => {
    // 实现语音输入功能
    console.log('语音输入功能待实现')
  }

  const handleImageInput = () => {
    // 实现图片搜索功能
    console.log('图片搜索功能待实现')
  }

  const toggleAdvancedOptions = () => {
    setShowAdvanced(!showAdvanced)
  }

  return (
    <div className={`search-input-container ${className}`} style={style}>
      {/* 主搜索输入框 */}
      <div className="search-input-main" style={{ marginBottom: showAdvanced ? 12 : 0 }}>
        <AutoComplete
          ref={inputRef}
          style={{ width: '100%' }}
          options={formattedOptions}
          onSelect={handleSuggestionSelect}
          onSearch={setInputValue}
          value={inputValue}
          open={inputValue.length > 0 && allSuggestions.length > 0}
        >
          <Search
            placeholder={placeholder}
            size={size}
            enterButton={
              <Button
                type="primary"
                icon={<SearchOutlined />}
                loading={loading}
                onClick={() => handleSearch()}
              >
                搜索
              </Button>
            }
            disabled={disabled}
            onKeyPress={handleKeyPress}
            suffix={
              <Space>
                {loading && <Spin size="small" />}
                {showHistory && inputValue.length === 0 && (
                  <Button
                    type="text"
                    size="small"
                    icon={<HistoryOutlined />}
                    onClick={() => setInputValue('')}
                    title="搜索历史"
                  />
                )}
              </Space>
            }
          />
        </AutoComplete>

        {/* 辅助功能按钮 */}
        <Space style={{ marginLeft: 8 }}>
          {showVoiceInput && (
            <Button
              type="text"
              size={size}
              icon={<AudioOutlined />}
              onClick={handleVoiceInput}
              title="语音搜索"
              disabled={disabled}
            />
          )}

          {showImageInput && (
            <Button
              type="text"
              size={size}
              icon={<CameraOutlined />}
              onClick={handleImageInput}
              title="图片搜索"
              disabled={disabled}
            />
          )}

          {showAdvancedOptions && (
            <Button
              type="text"
              size={size}
              icon={<SettingOutlined />}
              onClick={toggleAdvancedOptions}
              title="高级搜索选项"
              disabled={disabled}
            />
          )}
        </Space>
      </div>

      {/* 高级搜索选项 */}
      {showAdvanced && (
        <div className="search-advanced-options" style={{
          padding: 12,
          background: '#f5f5f5',
          borderRadius: 6,
          border: '1px solid #d9d9d9'
        }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* AI搜索开关 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>AI智能搜索</span>
              <Button
                type={searchOptions.useAI ? 'primary' : 'default'}
                size="small"
                onClick={() => setSearchOptions(prev => ({
                  ...prev,
                  useAI: !prev.useAI
                }))}
              >
                {searchOptions.useAI ? '开启' : '关闭'}
              </Button>
            </div>

            {/* 排序方式 */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>排序方式</span>
              <Button
                size="small"
                onClick={() => {
                  const sortOptions = ['relevance', 'date', 'name', 'size']
                  const currentIndex = sortOptions.indexOf(searchOptions.sortBy || 'relevance')
                  const nextIndex = (currentIndex + 1) % sortOptions.length
                  setSearchOptions(prev => ({
                    ...prev,
                    sortBy: sortOptions[nextIndex]
                  }))
                }}
              >
                {
                  searchOptions.sortBy === 'relevance' ? '相关度' :
                  searchOptions.sortBy === 'date' ? '日期' :
                  searchOptions.sortBy === 'name' ? '名称' : '大小'
                }
              </Button>
            </div>

            {/* 清除搜索历史 */}
            {showHistory && (
              <div style={{ textAlign: 'right' }}>
                <Button
                  type="text"
                  size="small"
                  icon={<ClearOutlined />}
                  onClick={clearHistory}
                >
                  清除搜索历史
                </Button>
              </div>
            )}
          </Space>
        </div>
      )}
    </div>
  )
}

export default SearchInput