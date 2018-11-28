//
//  ImageViewController.swift
//  PAMApp
//
//  Created by Jackson Quick on 11/27/18.
//  Copyright © 2018 Jackson Quick. All rights reserved.
//

import UIKit


class ImageViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
    
    var imageStr = ""
    var resultText = ""


    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    @IBOutlet weak var imageViewOne: UIImageView!
    

    @IBAction func onPickImage(_ sender: Any) {
        let image = UIImagePickerController()
        image.delegate = self
        
        image.sourceType = UIImagePickerController.SourceType.photoLibrary
        
        image.allowsEditing = false
        
        self.present(image, animated: true)
        {
            // unneeded currently
        }
    }
    
    @IBAction func didPressPam(_ sender: Any) {
        
        
        let parameters = ["results": "ATGCCA[TCC]", "nucleases": "SpCas9", "image": imageStr]

        
        guard let url = URL(string: "http://127.0.0.1:5000/iosappimagepost") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        guard let httpBody = try? JSONSerialization.data(withJSONObject: parameters, options: []) else { return }
        request.httpBody = httpBody
        
        let session = URLSession.shared
        session.dataTask(with: request) { (data, response, error) in
            if let response = response {
                print(response)
            }
            
            if let data = data {
                let jsonResult = try! JSONDecoder().decode(Results.self, from: data)
                print("\(jsonResult.modSequence)")
                self.resultText = jsonResult.modSequence
            }
        }.resume()
        
        self.performSegue(withIdentifier: "resultssegue", sender: self)
        
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
       
        print(self.resultText)
    }
    
    struct Results: Decodable {
        let modSequence: String
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        
        let image = info[UIImagePickerController.InfoKey.originalImage] as? UIImage
        imageViewOne.image = image
        let imageData:Data = image!.pngData()!
        imageStr = imageData.base64EncodedString()
        self.dismiss(animated: true, completion: nil)
        
    }
    
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
