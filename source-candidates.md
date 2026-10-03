# 収集対象サイトの候補

作成日：2026-10-03。採用前の候補一覧。各サイト名のリンクは参照元を兼ねる。

## 選定方針

公式発表で変更を把握し、企業ブログで実践例を読み、投稿サイトやブックマークで新しい話題を発見する構成を提案する。日本語・英語の両方を対象にする。

IT界隈で流行っていることや、気軽に読める記事も収集対象にする。個人の体験談、エンジニアの働き方、話題のサービス・ガジェット、趣味の開発、技術にまつわる雑談なども含める。公式情報と同じく、話題の発見を初期導入から重視する。

優先度は提案であり、採用確定ではない。SRE、AWS、Terraform / Terragrunt、GitLab CI/CDとの関連を基準に、Aは初期導入候補、Bは追加候補、Cは関心分野に応じた候補とする。技術全般への広がりも残す。

## 1. 公式・技術団体・OSS

| サイト | 言語 | 主な用途・選定理由 | 優先度 |
| --- | --- | --- | --- |
| [AWS What's New](https://aws.amazon.com/new/) | 英語 | サービスの新機能・リージョン拡大などの公式発表 | A |
| [AWS 日本語ブログ](https://aws.amazon.com/jp/blogs/news/) | 日本語 | AWSの解説・事例を日本語で追う | A |
| [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/) | 英語 | クラウドの設計パターン・構成事例 | B |
| [Google Cloud Blog](https://cloud.google.com/blog/) | 英語中心 | Google Cloudの発表・技術解説 | A |
| [Microsoft Dev Blogs](https://devblogs.microsoft.com/) | 英語 | Microsoftの開発者向け情報。対象ブログは導入時に絞る | A |
| [Apple Developer News](https://developer.apple.com/news/) | 英語 | Appleプラットフォーム・開発ツールの更新 | C |
| [HashiCorp Blog](https://www.hashicorp.com/en/blog) | 英語 | Terraform・Vaultなどの製品情報 | A |
| [GitLab Blog](https://about.gitlab.com/blog/) | 英語 | CI/CD・DevSecOpsの情報。技術記事を選別する | A |
| [Terragrunt Releases](https://github.com/gruntwork-io/terragrunt/releases) | 英語 | ブログとは別に、利用ツールの変更を直接追う | A |
| [Kubernetes Blog](https://kubernetes.io/blog/) | 英語 | Kubernetesの公式解説・更新情報 | B |
| [CNCF Blog](https://www.cncf.io/blog/) | 英語 | クラウドネイティブ技術・コミュニティの動向 | B |

公式ブログに加えて、実際に利用するOSSのリリースノート・セキュリティ告知を登録すると、実務で対応が必要な変更を拾いやすい。対象製品とバージョンは今後決める。団体サイトでも寄稿やスポンサー記事があるため、記事単位で出典と性質を確認する。

## 2. アメリカのビッグテック・海外テック企業

Amazon / AWS、Google、Microsoft、Appleは上の公式枠に記載。ここでは、企業自身の設計・運用経験を読む候補を挙げる。

| サイト | 言語 | 主な用途・選定理由 | 優先度 |
| --- | --- | --- | --- |
| [Engineering at Meta](https://engineering.fb.com/) | 英語 | 大規模サービスの基盤・性能・分散システムの事例 | B |
| [Netflix TechBlog](https://netflixtechblog.com/) | 英語 | 配信基盤・信頼性・データ基盤の事例 | B |
| [Cloudflare Blog](https://blog.cloudflare.com/) | 英語中心 | ネットワーク・セキュリティ・性能・運用の事例 | A |
| [GitHub Engineering](https://github.blog/engineering/) | 英語 | 開発基盤・大規模サービスの設計と運用 | B |
| [Engineering@Microsoft](https://devblogs.microsoft.com/engineering-at-microsoft/) | 英語 | Microsoft社内のエンジニアリング事例 | B |

## 3. 日本の企業テックブログ

| サイト | 言語 | 主な用途・選定理由 | 優先度 |
| --- | --- | --- | --- |
| [DevelopersIO](https://dev.classmethod.jp/) | 日本語中心 | AWSを中心とした検証・実装記事 | A |
| [LINEヤフー Tech Blog](https://techblog.lycorp.co.jp/ja) | 日本語 | 大規模サービスの開発・基盤運用の事例 | B |
| [CyberAgent Developers Blog](https://developers.cyberagent.co.jp/blog/) | 日本語 | サービス開発・インフラ・データ活用の事例 | B |
| [Hatena Developer Blog](https://developer.hatenastaff.com/) | 日本語 | Webサービスの開発・運用の事例 | B |
| [SmartHR Tech Blog](https://tech.smarthr.jp/) | 日本語 | SaaSの開発・運用・開発組織の事例 | B |
| [Mercari Engineering](https://tech.mercari.com/) | 日本語・英語 | 開発・基盤の事例を読む候補。今回のWeb取得では内容未確認 | B |

## 4. 個人投稿・コミュニティ・話題の発見

| サイト | 言語 | 主な用途・選定理由 | 優先度 |
| --- | --- | --- | --- |
| [Zenn](https://zenn.dev/) | 日本語中心 | 個人・企業の技術記事。トピック別や著者別の収集も検討 | A |
| [Qiita](https://qiita.com/) | 日本語中心 | 個人・企業の実装・検証記事。今回のWeb取得では内容未確認 | A |
| [はてなブックマーク：テクノロジー](https://b.hatena.ne.jp/hotentry/it) | 日本語中心 | IT界隈で話題の技術・サービス、個人ブログ、体験談を発見する入口 | A |
| [はてなブックマーク：総合（全カテゴリ）](https://b.hatena.ne.jp/hotentry/all) | 日本語中心 | カテゴリをまたぐ流行やカジュアルな話題を発見し、IT・ネット文化に関係する記事を拾う | A |
| [Hacker News](https://news.ycombinator.com/) | 英語中心 | 海外の技術・OSS・スタートアップ、個人の開発や議論を発見する入口 | A |

Zenn・Qiitaには企業発信も含まれる。個人の独立ブログは、上記で見つけた記事から著者を選び、継続して読みたいブログを個別登録する方法を提案する。はてなブックマークやHacker Newsでは、リンク先の記事を情報源として扱い、人気と技術的な正確さは別に評価する。

はてなブックマークは「テクノロジー」と「総合」の人気エントリーを両方対象にする。「全」は総合（全カテゴリ）として扱う。総合からはIT、AI、ネット文化、ガジェット、エンジニアの仕事などに関係する話題を選び、テクノロジーと重なる記事はまとめる。

通知では「IT界隈の話題・読みもの」も設け、話題がある日は数件を掲載する構成を提案する。公式の新機能発表だけで通知枠が埋まらないようにし、面白い個人開発や体験談も選ぶ。記事数や配分は試験収集後に調整する。

## 5. 追加提案：技術ニュース・週刊まとめ・セキュリティ

| サイト | 言語 | 主な用途・選定理由 | 優先度 |
| --- | --- | --- | --- |
| [Publickey](https://www.publickey1.jp/) | 日本語 | クラウド・開発ツールなどの動向を横断的に把握する | A |
| [InfoQ 日本語版](https://www.infoq.com/jp/) | 日本語 | ソフトウェア設計・アーキテクチャ・開発手法の情報 | B |
| [SRE Weekly](https://sreweekly.com/) | 英語 | 信頼性・障害対応・自動化などの記事を週刊で発見する | A |
| [JPCERT/CC 注意喚起](https://www.jpcert.or.jp/at/) | 日本語 | 運用上の対応につながるセキュリティ情報 | A |

この4種類を加えると、新機能や実装記事に加えて、分野横断の動向、設計判断、運用上の教訓、セキュリティ対応をカバーできる。

## 最初に試す構成

まずは次の14の収集先で、記事量と有用性を確認することを提案する。はてなブックマークはカテゴリ別に数える。

1. AWS What's New
2. AWS 日本語ブログ
3. Google Cloud Blog
4. Microsoft Dev Blogs（対象ブログを絞る）
5. HashiCorp Blog
6. GitLab Blog
7. Cloudflare Blog
8. DevelopersIO
9. Zenn
10. Qiita
11. はてなブックマーク：テクノロジー
12. はてなブックマーク：総合（全カテゴリ）
13. Hacker News
14. Publickey

海外の運用事例を重視する場合は、Meta・Netflix・SRE Weeklyを追加する。利用ツールの更新やセキュリティ対応も通知対象にする場合は、Terragrunt Releases・JPCERT/CCを追加する。

## 確認済み事項と今後の作業

- 2026-10-03にWebで各候補のページを参照。QiitaとMercari Engineeringは取得エラーのため内容未確認。それ以外はページの取得を確認した。
- 言語は主な掲載言語の目安。優先度と選定理由は本プロジェクトへの適合性についての提案。
- 実装した11フィードは[config/sources.json](config/sources.json)に記載。2026-10-03にRSS / Atomの実取得と再取得を確認した。Qiitaもフィード取得は成功した。候補一覧の残りのサイトのフィード、利用条件、長期の継続取得の可否は未確認。表の候補URLは収集エンドポイントではない。
- 採用時はRSS / Atomを優先して調査し、取得方法・対象カテゴリ・タグ・著者・通知条件を決める。
- 翻訳記事、転載、集約サイト経由の同一記事は重複をまとめる。新機能、実践記事、セキュリティ情報は通知目的に応じて扱いを決める。
