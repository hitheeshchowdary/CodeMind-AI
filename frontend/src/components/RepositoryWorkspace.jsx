import {

  useEffect,

  useMemo,

  useRef,

  useState,

} from 'react'



import {

  askRepositoryQuestion,

} from '../services/chatService'





const CHAT_STORAGE_KEY =

  'codemind_repository_chat_histories_v2'





/* =========================================================
   QUESTION SUGGESTION ENGINE
   ========================================================= */

function normalizeText(value = '') {
  return String(value)
    .toLowerCase()
    .replace(/[_\-./\\]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function uniqueStrings(items) {
  return [...new Set(
    items
      .map((item) => String(item || '').trim())
      .filter(Boolean),
  )]
}

function getRepositorySignals(repository) {
  const files = Array.isArray(repository?.files)
    ? repository.files
    : []

  const languages = Array.isArray(repository?.languages)
    ? repository.languages
    : []

  const filePaths = uniqueStrings(
    files.map((file) => getFilePath(file)),
  )

  const fileNames = uniqueStrings(
    filePaths.map((filePath) => getDisplayFileName(filePath)),
  )

  const normalizedFiles = filePaths.map(normalizeText)
  const normalizedNames = fileNames.map(normalizeText)
  const normalizedLanguages = languages.map(normalizeText)

  const hasAny = (...terms) =>
    [...normalizedFiles, ...normalizedNames].some((value) =>
      terms.some((term) => value.includes(term)),
    )

  return {
    filePaths,
    fileNames,
    normalizedFiles,
    normalizedNames,
    normalizedLanguages,
    fileCount: filePaths.length,
    languageCount: languages.length,
    hasPython: normalizedLanguages.some((value) =>
      value.includes('python'),
    ),
    hasJava: normalizedLanguages.some((value) =>
      value.includes('java'),
    ),
    hasJavaScript: normalizedLanguages.some((value) =>
      value.includes('javascript') ||
      value.includes('typescript'),
    ),
    hasReact: normalizedLanguages.some((value) =>
      value.includes('react'),
    ) || hasAny('react'),
    hasDatabase: hasAny(
      'database',
      'db',
      'model',
      'repository',
      'schema',
      'sql',
      'mongo',
    ),
    hasApi: hasAny(
      'api',
      'route',
      'router',
      'controller',
      'endpoint',
      'fastapi',
      'flask',
      'express',
      'spring',
    ),
    hasAuth: hasAny(
      'auth',
      'login',
      'user',
      'permission',
      'security',
      'token',
      'jwt',
    ),
    hasParser: hasAny(
      'parser',
      'parse',
      'extract',
      'processor',
    ),
    hasServiceLayer: hasAny(
      'service',
      'services',
      'usecase',
      'usecases',
    ),
    hasTestFiles: hasAny(
      'test',
      'tests',
      'spec',
    ),
    hasConfig: hasAny(
      'config',
      'settings',
      'env',
      'requirements',
      'package',
      'pom',
      'docker',
    ),
    hasUi: hasAny(
      'component',
      'components',
      'frontend',
      'pages',
      'views',
      'templates',
      'html',
      'css',
      'jsx',
      'tsx',
    ),
    hasMainFile: normalizedNames.some((name) =>
      ['app py', 'main py', 'index js', 'index jsx', 'app js', 'app jsx']
        .some((candidate) => name === candidate),
    ),
  }
}

function getFileCandidates(signals, terms) {
  return signals.fileNames.filter((fileName) =>
    terms.some((term) => fileName.toLowerCase().includes(term)),
  )
}

function buildQuestionSuggestions({
  repository,
  currentQuestion = '',
  currentAnswer = '',
  previousMessages = [],
  count = 5,
}) {
  const signals = getRepositorySignals(repository)
  const question = normalizeText(currentQuestion)
  const answer = normalizeText(currentAnswer)

  const previousQuestions = new Set(
    previousMessages
      .filter((message) => message?.role === 'user')
      .map((message) => normalizeText(message.content)),
  )

  const candidates = []

  const add = (
    text,
    category,
    score = 0,
    evidence = false,
  ) => {
    const normalized = normalizeText(text)

    if (
      !normalized ||
      normalized === question ||
      previousQuestions.has(normalized)
    ) {
      return
    }

    candidates.push({
      text,
      category,
      score: score + (evidence ? 8 : 0),
    })
  }

  /*
   * Every repository gets a small set of high-value exploration
   * questions. These are deliberately deterministic and cheap.
   */
  add(
    'Which files are most important to understanding this project?',
    'exploration',
    7,
    signals.fileCount > 0,
  )

  add(
    'What is the main execution flow of this project?',
    'workflow',
    8,
    signals.fileCount > 1,
  )

  add(
    'Which file contains the main application logic?',
    'code',
    7,
    signals.hasMainFile,
  )

  add(
    'How do the main components of this project interact?',
    'architecture',
    8,
    signals.fileCount > 1,
  )

  add(
    'What are the main technologies and frameworks used here?',
    'technology',
    7,
    signals.languageCount > 0,
  )

  /*
   * Repository-grounded feature questions.
   */
  if (signals.hasApi) {
    add(
      'How does the API layer work in this project?',
      'api',
      14,
      true,
    )

    add(
      'Which files define the main API routes or endpoints?',
      'api',
      12,
      true,
    )
  }

  if (signals.hasAuth) {
    add(
      'How is authentication or user authorization handled?',
      'security',
      14,
      true,
    )
  }

  if (signals.hasDatabase) {
    add(
      'How does this project store and manage data?',
      'data',
      14,
      true,
    )

    add(
      'Which files are responsible for database or data access?',
      'data',
      12,
      true,
    )
  }

  if (signals.hasParser) {
    add(
      'How does the parsing or data extraction process work?',
      'processing',
      15,
      true,
    )

    const parserFiles = getFileCandidates(
      signals,
      ['parser', 'parse', 'extract'],
    )

    if (parserFiles.length === 1) {
      add(
        `What is the role of ${parserFiles[0]} in this project?`,
        'code',
        18,
        true,
      )
    }
  }

  if (signals.hasServiceLayer) {
    add(
      'What responsibilities are handled by the service layer?',
      'architecture',
      13,
      true,
    )
  }

  if (signals.hasUi || signals.hasReact) {
    add(
      'How is the user interface organized?',
      'frontend',
      12,
      true,
    )

    if (signals.hasReact) {
      add(
        'How do the frontend components communicate with the backend?',
        'frontend',
        14,
        true,
      )
    }
  }

  if (signals.hasPython) {
    add(
      'How is the Python code organized across the repository?',
      'technology',
      10,
      true,
    )
  }

  if (signals.hasJava) {
    add(
      'How is the Java code organized across the repository?',
      'technology',
      10,
      true,
    )
  }

  if (signals.hasJavaScript) {
    add(
      'How is the JavaScript or TypeScript code organized?',
      'technology',
      10,
      true,
    )
  }

  if (signals.hasTestFiles) {
    add(
      'What tests are already available in this project?',
      'testing',
      12,
      true,
    )

    add(
      'Which important parts of the project are not covered by tests?',
      'testing',
      9,
      true,
    )
  }

  if (signals.hasConfig) {
    add(
      'Where is the project configuration defined?',
      'configuration',
      10,
      true,
    )
  }

  /*
   * Follow-ups based on the current question.
   * These are deliberately different from the repository-wide defaults.
   */
  if (
    question.includes('architecture') ||
    question.includes('workflow') ||
    question.includes('flow')
  ) {
    add(
      'Which files participate in this workflow?',
      'architecture',
      18,
    )

    add(
      'What happens first, and what happens next in this flow?',
      'workflow',
      16,
    )

    add(
      'Where is the most important business logic for this flow?',
      'code',
      15,
    )
  }

  if (
    question.includes('what does') ||
    question.includes('purpose') ||
    question.includes('project do') ||
    question.includes('overview')
  ) {
    add(
      'Which files implement the core functionality described above?',
      'code',
      18,
    )

    add(
      'What is the end-to-end workflow of the main feature?',
      'workflow',
      17,
    )

    add(
      'Which component is responsible for the main functionality?',
      'architecture',
      15,
    )
  }

  if (
    question.includes('technology') ||
    question.includes('framework') ||
    question.includes('library') ||
    question.includes('dependencies')
  ) {
    add(
      'Where is each major technology used in the codebase?',
      'technology',
      18,
    )

    add(
      'Which dependencies are most important to the application?',
      'technology',
      16,
    )
  }

  if (
    question.includes('file') ||
    question.includes('function') ||
    question.includes('class') ||
    question.includes('code')
  ) {
    add(
      'How does this code interact with the rest of the repository?',
      'code',
      18,
    )

    add(
      'What other files depend on this implementation?',
      'architecture',
      17,
    )

    add(
      'What happens when this code is executed?',
      'workflow',
      15,
    )
  }

  /*
   * Improvement questions are useful, but only after the user has
   * already explored the repository. This prevents the first follow-up
   * from immediately becoming generic "how can I improve it?" advice.
   */
  const hasConversation = previousMessages.some(
    (message) => message?.role === 'assistant',
  )

  if (hasConversation || answer.length > 0) {
    add(
      'What are the main limitations or potential weaknesses in this implementation?',
      'engineering',
      10,
    )

    add(
      'What part of this project would benefit most from refactoring?',
      'engineering',
      9,
    )

    if (signals.hasTestFiles) {
      add(
        'What additional tests would improve the reliability of this project?',
        'testing',
        11,
      )
    }
  }

  /*
   * Light answer-aware boosts. We don't trust the answer as evidence;
   * it only helps choose a better follow-up category.
   */
  const answerBoostTerms = {
    api: ['api', 'endpoint', 'route'],
    data: ['database', 'data', 'storage'],
    security: ['authentication', 'authorization', 'login', 'security'],
    workflow: ['workflow', 'process', 'flow'],
    architecture: ['architecture', 'component', 'module'],
    code: ['function', 'class', 'implementation'],
  }

  candidates.forEach((candidate) => {
    const terms = answerBoostTerms[candidate.category] || []

    if (terms.some((term) => answer.includes(term))) {
      candidate.score += 4
    }
  })

  /*
   * Prefer high-value repository-grounded suggestions while enforcing
   * category diversity so five buttons don't all ask the same thing.
   */
  candidates.sort((a, b) => b.score - a.score)

  const selected = []
  const usedCategories = new Set()

  for (const candidate of candidates) {
    if (selected.length >= count) {
      break
    }

    if (!usedCategories.has(candidate.category)) {
      selected.push(candidate.text)
      usedCategories.add(candidate.category)
    }
  }

  /*
   * If category diversity exhausted the candidate pool, fill remaining
   * slots with the next highest-scoring unique suggestions.
   */
  if (selected.length < count) {
    for (const candidate of candidates) {
      if (selected.length >= count) {
        break
      }

      if (!selected.includes(candidate.text)) {
        selected.push(candidate.text)
      }
    }
  }

  return selected.slice(0, count)
}

/* =========================================================

   COMPONENT

   ========================================================= */



function RepositoryWorkspace({

  repository,

  projects = [],

  onNewProject,

  onSelectProject,

  onRemoveProject,

}) {

  const textareaRef = useRef(null)



  const chatEndRef = useRef(null)



  const messageIdRef = useRef(0)





  const repositoryName =

    repository?.repository_name ||

    'repository'





  /* =======================================================

     STATE

     ======================================================= */



  const [question, setQuestion] =

    useState('')



  const [isAsking, setIsAsking] =

    useState(false)



  const [error, setError] =

    useState('')





  const [

    chatHistories,

    setChatHistories,

  ] = useState(() => {

    try {

      const savedHistories =

        localStorage.getItem(

          CHAT_STORAGE_KEY,

        )



      if (!savedHistories) {

        return {}

      }



      const parsedHistories =

        JSON.parse(savedHistories)



      if (

        parsedHistories &&

        typeof parsedHistories ===

          'object' &&

        !Array.isArray(parsedHistories)

      ) {

        return parsedHistories

      }



      return {}

    } catch (storageError) {

      console.error(

        'Unable to load chat histories:',

        storageError,

      )



      return {}

    }

  })





  const messages =

    chatHistories[repositoryName] || []





  const files = Array.isArray(

    repository?.files,

  )

    ? repository.files

    : []





  const languages = Array.isArray(

    repository?.languages,

  )

    ? repository.languages

    : []





  /*

   * Initial suggestions are deterministic.

   * Math.random() is NOT used during rendering.

   */

  const initialSuggestions = useMemo(
    () =>
      buildQuestionSuggestions({
        repository,
        count: 5,
      }),
    [repository],
  )





  const getNextMessageId = () => {

    messageIdRef.current += 1



    return `message-${messageIdRef.current}`

  }





  /* =======================================================

     CHAT HISTORY STORAGE

     ======================================================= */



  useEffect(() => {

    try {

      localStorage.setItem(

        CHAT_STORAGE_KEY,

        JSON.stringify(chatHistories),

      )

    } catch (storageError) {

      console.error(

        'Unable to save chat histories:',

        storageError,

      )

    }

  }, [chatHistories])





  /* =======================================================

     AUTO SCROLL

     ======================================================= */



  useEffect(() => {

    chatEndRef.current?.scrollIntoView({

      behavior: 'smooth',

      block: 'nearest',

    })

  }, [messages.length, isAsking])





  /* =======================================================

     TEXTAREA AUTO RESIZE

     ======================================================= */



  const resizeTextarea = () => {

    const textarea =

      textareaRef.current



    if (!textarea) {

      return

    }



    textarea.style.height = 'auto'



    const maximumHeight = 120



    const newHeight = Math.min(

      textarea.scrollHeight,

      maximumHeight,

    )



    textarea.style.height =

      `${newHeight}px`



    textarea.style.overflowY =

      textarea.scrollHeight >

      maximumHeight

        ? 'auto'

        : 'hidden'

  }





  useEffect(() => {

    requestAnimationFrame(() => {

      resizeTextarea()

    })

  }, [question])





  /* =======================================================

     ADD MESSAGE

     ======================================================= */



  const addMessage = (message) => {

    setChatHistories(

      (currentHistories) => {

        const currentMessages =

          currentHistories[

            repositoryName

          ] || []



        return {

          ...currentHistories,



          [repositoryName]: [

            ...currentMessages,

            message,

          ],

        }

      },

    )

  }





  /* =======================================================

     REMOVE CHAT HISTORY

     ======================================================= */



  const removeChatHistory = (

    projectName,

  ) => {

    setChatHistories(

      (currentHistories) => {

        const updatedHistories = {

          ...currentHistories,

        }



        delete updatedHistories[

          projectName

        ]



        try {

          localStorage.setItem(

            CHAT_STORAGE_KEY,

            JSON.stringify(

              updatedHistories,

            ),

          )

        } catch (storageError) {

          console.error(

            'Unable to remove chat history:',

            storageError,

          )

        }



        return updatedHistories

      },

    )

  }





  /* =======================================================

     ASK QUESTION

     ======================================================= */



  const handleAskQuestion = async (

    providedQuestion = question,

  ) => {

    const trimmedQuestion =

      String(

        providedQuestion || '',

      ).trim()



    if (

      !trimmedQuestion ||

      isAsking

    ) {

      return

    }





    const userMessage = {

      id: getNextMessageId(),



      role: 'user',



      content: trimmedQuestion,

    }





    addMessage(userMessage)



    setQuestion('')

    setError('')

    setIsAsking(true)





    try {

      const data =

        await askRepositoryQuestion({

          repositoryName,



          question:

            trimmedQuestion,



          topK: 5,

        })





      const assistantMessage = {

        id: getNextMessageId(),



        role: 'assistant',



        content:

          data?.answer ||

          'I could not find an answer in this repository.',



        sources: Array.isArray(

          data?.sources,

        )

          ? data.sources

          : [],



        /*

         * Random suggestions are generated

         * inside an event handler, not render.

         */

        suggestions:
          buildQuestionSuggestions({
            repository,
            currentQuestion: trimmedQuestion,
            currentAnswer: data?.answer || '',
            previousMessages: messages,
            count: 5,
          }),

      }





      addMessage(

        assistantMessage,

      )

    } catch (chatError) {

      console.error(

        'Chat error:',

        chatError,

      )



      const errorMessage =

        chatError?.message ||

        'Unable to get an answer from CodeMind AI.'



      setError(errorMessage)





      const assistantErrorMessage = {

        id: getNextMessageId(),



        role: 'assistant',



        content:

          errorMessage,



        sources: [],



        suggestions: [],



        isError: true,

      }





      addMessage(

        assistantErrorMessage,

      )

    } finally {

      setIsAsking(false)



      window.setTimeout(() => {

        textareaRef.current?.focus()

      }, 0)

    }

  }





  /* =======================================================

     KEYBOARD HANDLING

     ======================================================= */



  const handleKeyDown = (event) => {

    if (

      event.key === 'Enter' &&

      !event.shiftKey

    ) {

      event.preventDefault()



      handleAskQuestion()

    }

  }





  /* =======================================================

     NEW CHAT

     ======================================================= */



  const handleNewChat = () => {

    if (isAsking) {

      return

    }



    const shouldClear =

      window.confirm(

        'Start a new chat? Your current chat history for this repository will be cleared.',

      )



    if (!shouldClear) {

      return

    }



    removeChatHistory(

      repositoryName,

    )



    setQuestion('')

    setError('')



    window.setTimeout(() => {

      textareaRef.current?.focus()

    }, 0)

  }





  /* =======================================================

     REMOVE PROJECT

     ======================================================= */



  const handleRemoveProject = (

    projectName,

    event,

  ) => {

    event.stopPropagation()



    if (!projectName) {

      return

    }



    const shouldRemove =

      window.confirm(

        `Remove "${projectName}" from your projects?`,

      )



    if (!shouldRemove) {

      return

    }



    removeChatHistory(projectName)



    onRemoveProject?.(

      projectName,

    )

  }





  /* =======================================================

     RENDER

     ======================================================= */



  return (

    <div className="workspace">



      <header className="workspace-header">



        <div className="workspace-brand">



          <div className="workspace-brand-mark">

            <span>

              &lt;/&gt;

            </span>

          </div>



          <div className="workspace-brand-text">



            <span className="workspace-brand-name">

              CodeMind

            </span>



            <span className="workspace-brand-ai">

              AI

            </span>



          </div>



        </div>





        <div className="workspace-repository">



          <span className="repository-status-dot" />



          <span className="repository-name">

            {repositoryName}

          </span>



          <span className="indexed-badge">

            Indexed

          </span>



        </div>





        <div className="workspace-actions">



          <button

            type="button"

            className="header-action-button"

            onClick={handleNewChat}

            disabled={isAsking}

          >

            + New Chat

          </button>





          <button

            type="button"

            className="header-action-button primary-header-action"

            onClick={onNewProject}

            disabled={isAsking}

          >

            + New Project

          </button>



        </div>



      </header>





      <div className="workspace-body">



        <aside className="repository-sidebar">



          <div className="projects-section">



            <div className="projects-heading">



              <span>

                Your Projects

              </span>





              <button

                type="button"

                className="sidebar-new-project-button"

                onClick={onNewProject}

                disabled={isAsking}

              >



                <span className="new-project-plus">

                  +

                </span>



                <span>

                  New

                </span>



              </button>



            </div>





            <div className="projects-list">



              {projects.length === 0 ? (



                <div className="no-projects">

                  No projects yet

                </div>



              ) : (



                projects.map(

                  (project) => {

                    const projectName =

                      project?.repository_name



                    const isActive =

                      projectName ===

                      repositoryName



                    if (!projectName) {

                      return null

                    }



                    return (

                      <div

                        className={`project-item ${

                          isActive

                            ? 'project-item-active'

                            : ''

                        }`}

                        key={projectName}

                      >



                        <button

                          type="button"

                          className="project-select-button"

                          onClick={() =>

                            onSelectProject?.(

                              project,

                            )

                          }

                          disabled={isAsking}

                        >



                          <span className="project-icon">

                            ◇

                          </span>



                          <span className="project-name">

                            {projectName}

                          </span>



                        </button>





                        <button

                          type="button"

                          className="project-remove-button"

                          onClick={(event) =>

                            handleRemoveProject(

                              projectName,

                              event,

                            )

                          }

                          disabled={isAsking}

                          aria-label={

                            `Remove ${projectName}`

                          }

                          title="Remove project"

                        >

                          ×

                        </button>



                      </div>

                    )

                  },

                )



              )}



            </div>



          </div>





          <div className="sidebar-heading">



            <span>

              Current Repository

            </span>



            <span className="file-count">

              {repository?.total_files ||

                files.length}{' '}

              files

            </span>



          </div>





          <div className="repository-tree">



            <div className="tree-item tree-folder">



              <span className="tree-chevron">

                ›

              </span>



              <span className="tree-icon">

                ▱

              </span>



              <span>

                Source files

              </span>



            </div>





            {files.slice(0, 12).map(

              (file, index) => (

                <div

                  className="tree-item tree-file"

                  key={`${getFilePath(

                    file,

                  )}-${index}`}

                >



                  <span className="tree-file-icon">

                    {getFileExtension(

                      file,

                    )}

                  </span>



                  <span className="tree-file-name">

                    {getDisplayFileName(

                      file,

                    )}

                  </span>



                </div>

              ),

            )}





            {files.length > 12 && (



              <div className="tree-more">

                +{files.length - 12} more files

              </div>



            )}



          </div>





          <div className="sidebar-bottom">



            <div className="sidebar-section-label">

              Languages

            </div>





            <div className="workspace-language-list">



              {languages.length > 0 ? (



                languages.map(

                  (language) => (

                    <span

                      className="workspace-language"

                      key={language}

                    >

                      {language}

                    </span>

                  ),

                )



              ) : (



                <span className="workspace-language">

                  Not detected

                </span>



              )}



            </div>



          </div>



        </aside>





        <main className="workspace-main">



          {messages.length === 0 ? (



            <div className="workspace-welcome">



              <div className="assistant-mark">

                <span>

                  ✦

                </span>

              </div>





              <h1>

                Ask anything about your codebase.

              </h1>





              <p>

                CodeMind AI searches your repository

                and uses the most relevant code to

                answer your questions.

              </p>





              <div className="example-questions">



                {initialSuggestions.map(

                  (suggestion) => (



                    <button

                      type="button"

                      key={suggestion}

                      onClick={() =>

                        handleAskQuestion(

                          suggestion,

                        )

                      }

                      disabled={isAsking}

                    >

                      {suggestion}

                    </button>



                  ),

                )}



              </div>



            </div>



          ) : (



            <div className="chat-history">



              {messages.map(

                (message) => (



                  <div

                    key={message.id}

                    className={`chat-message ${

                      message.role === 'user'

                        ? 'user-message'

                        : 'assistant-message'

                    }`}

                  >



                    {message.role === 'user' ? (



                      <div className="user-message-content">



                        <div className="message-label">

                          You

                        </div>



                        <div className="user-question">

                          {message.content}

                        </div>



                      </div>



                    ) : (



                      <div className="assistant-message-content">



                        <div className="assistant-message-header">



                          <div className="assistant-mark small">

                            <span>

                              ✦

                            </span>

                          </div>





                          <div>



                            <strong>

                              CodeMind AI

                            </strong>



                            <span>

                              {message.isError

                                ? 'Error'

                                : 'AI-generated answer'}

                            </span>



                          </div>



                        </div>





                        <div

                          className={`assistant-answer ${

                            message.isError

                              ? 'assistant-error-answer'

                              : ''

                          }`}

                        >

                          {message.content}

                        </div>





                        {message.sources?.length > 0 && (



                          <div className="message-sources">



                            <h4>

                              Relevant Sources

                            </h4>





                            {message.sources.map(

                              (

                                source,

                                index,

                              ) => (



                                <div

                                  className="source-card"

                                  key={`${getSourceName(

                                    source,

                                  )}-${index}`}

                                >



                                  <strong>

                                    {getSourceName(

                                      source,

                                    )}

                                  </strong>





                                  {getSourcePath(

                                    source,

                                  ) && (



                                    <span className="source-path">



                                      {getSourcePath(

                                        source,

                                      )}



                                    </span>



                                  )}





                                  {getSourceRelevance(

                                    source,

                                  ) !== null && (



                                    <span className="source-relevance">



                                      Relevance:{' '}



                                      {getSourceRelevance(

                                        source,

                                      ).toFixed(3)}



                                    </span>



                                  )}



                                </div>



                              ),

                            )}



                          </div>



                        )}





                        {!message.isError &&

                          message.suggestions?.length >

                            0 && (



                            <div className="follow-up-suggestions">



                              <span className="suggestions-title">

                                You can also ask

                              </span>





                              <div className="suggestion-buttons">



                                {message.suggestions.map(

                                  (

                                    suggestion,

                                  ) => (



                                    <button

                                      type="button"

                                      key={`${message.id}-${suggestion}`}

                                      onClick={() =>

                                        handleAskQuestion(

                                          suggestion,

                                        )

                                      }

                                      disabled={

                                        isAsking

                                      }

                                    >

                                      {suggestion}

                                    </button>



                                  ),

                                )}



                              </div>



                            </div>



                          )}



                      </div>



                    )}



                  </div>



                ),

              )}





              {isAsking && (



                <div className="chat-message assistant-message">



                  <div className="assistant-message-content">



                    <div className="assistant-message-header">



                      <div className="assistant-mark small">

                        <span>

                          ✦

                        </span>

                      </div>





                      <div>



                        <strong>

                          CodeMind AI

                        </strong>



                        <span>

                          Analyzing your codebase...

                        </span>



                      </div>



                    </div>





                    <div className="typing-indicator">



                      <span />



                      <span />



                      <span />



                    </div>



                  </div>



                </div>



              )}





              <div ref={chatEndRef} />



            </div>



          )}





          <div className="workspace-input-container">



            <div className="workspace-input">



              <textarea

                ref={textareaRef}

                value={question}

                onChange={(event) => {

                  setQuestion(

                    event.target.value,

                  )

                }}

                onKeyDown={handleKeyDown}

                placeholder="Ask a question about your code..."

                rows="1"

                disabled={isAsking}

              />





              <button

                className="send-button"

                type="button"

                onClick={() =>

                  handleAskQuestion()

                }

                disabled={

                  !question.trim() ||

                  isAsking

                }

                aria-label="Send question"

              >



                {isAsking

                  ? '…'

                  : '↑'}



              </button>



            </div>





            <div className="workspace-input-hint">



              <span>

                Enter to send

              </span>



              <span>

                Shift + Enter for a new line

              </span>



            </div>





            {error && (



              <div className="chat-error">

                {error}

              </div>



            )}



          </div>



        </main>



      </div>



    </div>

  )

}





/* =========================================================

   REPOSITORY FILE HELPERS

   ========================================================= */



function getFilePath(file) {

  if (typeof file === 'string') {

    return file

  }



  if (

    !file ||

    typeof file !== 'object'

  ) {

    return ''

  }



  return (

    file.path ||

    file.file ||

    file.name ||

    ''

  )

}





function getDisplayFileName(file) {

  const filePath =

    getFilePath(file)



  if (!filePath) {

    return 'Unknown file'

  }



  const normalizedPath =

    String(filePath).replaceAll(

      '\\\\',

      '/',

    )



  const parts =

    normalizedPath.split('/')



  return (

    parts[parts.length - 1] ||

    normalizedPath

  )

}





function getFileExtension(file) {

  const fileName =

    getDisplayFileName(file)



  const extension =

    fileName.includes('.')

      ? fileName.split('.').pop()

      : ''



  return extension

    ? extension

      .toUpperCase()

      .slice(0, 4)

    : 'FILE'

}





/* =========================================================

   SOURCE HELPERS

   ========================================================= */



function getSourceName(source) {

  if (typeof source === 'string') {

    return getFileNameFromPath(

      source,

    )

  }



  if (

    !source ||

    typeof source !== 'object'

  ) {

    return 'Unknown source'

  }



  return (

    source.filename ||

    source.file_name ||

    source.name ||

    source.file ||

    getFileNameFromPath(

      source.path ||

        source.file_path ||

        '',

    )

  )

}





function getSourcePath(source) {

  if (typeof source === 'string') {

    return source

  }



  if (

    !source ||

    typeof source !== 'object'

  ) {

    return ''

  }



  return (

    source.path ||

    source.file_path ||

    source.file ||

    ''

  )

}





function getSourceRelevance(source) {

  if (

    !source ||

    typeof source !== 'object'

  ) {

    return null

  }



  const value =

    source.relevance ??

    source.score ??

    source.similarity



  const numericValue =

    Number(value)



  return Number.isFinite(

    numericValue,

  )

    ? numericValue

    : null

}





function getFileNameFromPath(path) {

  if (!path) {

    return 'Unknown source'

  }



  const normalizedPath =

    String(path).replaceAll(

      '\\\\',

      '/',

    )



  const parts =

    normalizedPath.split('/')



  return (

    parts[parts.length - 1] ||

    normalizedPath

  )

}





export default RepositoryWorkspace